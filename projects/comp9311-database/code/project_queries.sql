------------------------------------------------------
-- COMP9311 26T1 Project 1
-- Name: Yiyang Zheng
------------------------------------------------------

-- Q1:
CREATE OR REPLACE VIEW Q1(unsw_id, student_name) AS
-- 找出通过了至少 15 门 COMP9XXX 科目的学生。
-- 这里要求的是这些 subject 在 2011 年开设过，而不是学生必须在 2011 年修读。
SELECT p.unswid, p.name
FROM people p
JOIN students st
  ON st.id = p.id
JOIN course_enrolments ce
  ON ce.student = st.id
JOIN courses c
  ON c.id = ce.course
JOIN subjects su
  ON su.id = c.subject
WHERE ce.mark >= 50
  AND su.code LIKE 'COMP9%'
  AND EXISTS (
    SELECT 1
    FROM courses c2011
    JOIN semesters se2011
      ON se2011.id = c2011.semester
    WHERE c2011.subject = su.id
      AND se2011.year = 2011
  )
GROUP BY p.id, p.unswid, p.name
HAVING COUNT(DISTINCT su.code) >= 15
;

-- Q2:
CREATE OR REPLACE VIEW Q2(subject_code, mark_difference) AS
-- 先分别算出 2008 和 2012 年每门课的通过学生平均分，
-- 再比较两年差值，保留 2012 至少高 10 分的科目。
SELECT y12.subject_code,
       ROUND(y12.avg_mark - y08.avg_mark, 2) AS mark_difference
FROM (
    SELECT su.code AS subject_code,
           AVG(ce.mark)::numeric AS avg_mark
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    JOIN semesters se
      ON se.id = c.semester
    WHERE ce.mark >= 50
      AND se.year = 2008
    GROUP BY su.code
    HAVING COUNT(*) >= 10
) y08
JOIN (
    SELECT su.code AS subject_code,
           AVG(ce.mark)::numeric AS avg_mark
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    JOIN semesters se
      ON se.id = c.semester
    WHERE ce.mark >= 50
      AND se.year = 2012
    GROUP BY su.code
    HAVING COUNT(*) >= 10
) y12
  ON y12.subject_code = y08.subject_code
WHERE y12.avg_mark - y08.avg_mark >= 10
;

-- Q3:
CREATE OR REPLACE VIEW Q3(staff_id, staff_name, faculty_name) AS
-- 只保留直接挂在 Faculty orgunit 上的 affiliation。
-- 然后要求该 staff 的所有 affiliation 都来自同一个 faculty，
-- 并且在该 faculty 下至少拥有 3 个不同 role。
SELECT p.unswid AS staff_id,
       p.name AS staff_name,
       MIN(fa.faculty_name) AS faculty_name
FROM (
    SELECT a.staff,
           a.role,
           ou.id AS faculty_id,
           ou.name AS faculty_name
    FROM affiliations a
    JOIN orgunits ou
      ON ou.id = a.orgunit
    JOIN orgunit_types ot
      ON ot.id = ou.utype
    WHERE ot.name = 'Faculty'
) fa
JOIN staff s
  ON s.id = fa.staff
JOIN people p
  ON p.id = s.id
GROUP BY fa.staff, p.unswid, p.name
HAVING COUNT(*) = (
           SELECT COUNT(*)
           FROM affiliations a
           WHERE a.staff = fa.staff
       )
   AND COUNT(DISTINCT fa.faculty_id) = 1
   AND COUNT(DISTINCT fa.role) >= 3
;

-- Q4:
CREATE OR REPLACE VIEW Q4(program_id, unsw_id, max_wam) AS
-- 先找 2010 年活跃的 program，
-- 再统计学生在相同 semester 下的 program enrolment 和课程 enrolment，
-- 只保留可计入 WAM 的课程，最后找每个 program 的最高 WAM。
SELECT bw.program AS program_id,
       p.unswid AS unsw_id,
       bw.max_wam
FROM (
    SELECT wi.program,
           wi.student,
           ROUND(SUM(wi.mark * wi.uoc)::numeric / NULLIF(SUM(wi.uoc), 0), 2) AS max_wam
    FROM (
        SELECT pe.program,
               pe.student,
               su.uoc,
               ce.mark
        FROM program_enrolments pe
        JOIN semesters se
          ON se.id = pe.semester
        JOIN courses c
          ON c.semester = pe.semester
        JOIN course_enrolments ce
          ON ce.course = c.id
         AND ce.student = pe.student
        JOIN subjects su
          ON su.id = c.subject
        WHERE pe.program IN (
                  SELECT DISTINCT pe2.program
                  FROM program_enrolments pe2
                  JOIN semesters se2
                    ON se2.id = pe2.semester
                  WHERE se2.year = 2010
              )
          AND se.year <= 2010
          AND ce.mark IS NOT NULL
          AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
    ) wi
    GROUP BY wi.program, wi.student
) bw
JOIN (
    SELECT sw.program,
           MAX(sw.max_wam) AS max_wam
    FROM (
        SELECT wi.program,
               wi.student,
               ROUND(SUM(wi.mark * wi.uoc)::numeric / NULLIF(SUM(wi.uoc), 0), 2) AS max_wam
        FROM (
            SELECT pe.program,
                   pe.student,
                   su.uoc,
                   ce.mark
            FROM program_enrolments pe
            JOIN semesters se
              ON se.id = pe.semester
            JOIN courses c
              ON c.semester = pe.semester
            JOIN course_enrolments ce
              ON ce.course = c.id
             AND ce.student = pe.student
            JOIN subjects su
              ON su.id = c.subject
            WHERE pe.program IN (
                      SELECT DISTINCT pe2.program
                      FROM program_enrolments pe2
                      JOIN semesters se2
                        ON se2.id = pe2.semester
                      WHERE se2.year = 2010
                  )
              AND se.year <= 2010
              AND ce.mark IS NOT NULL
              AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
        ) wi
        GROUP BY wi.program, wi.student
    ) sw
    GROUP BY sw.program
) best
  ON best.program = bw.program
 AND best.max_wam = bw.max_wam
JOIN people p
  ON p.id = bw.student
ORDER BY bw.program, bw.max_wam DESC, p.unswid
LIMIT 50
;

-- Q5:
CREATE OR REPLACE VIEW Q5(room_id, distinct_course_count) AS
-- 先找“某个 semester 内至少承载 15 门不同 course 且覆盖至少 4 种 class type”的房间，
-- 然后统计这些房间在整个历史里一共承载过多少不同 course。
SELECT r.id AS room_id,
       COUNT(DISTINCT cl.course) AS distinct_course_count
FROM rooms r
JOIN classes cl
  ON cl.room = r.id
WHERE EXISTS (
          SELECT 1
          FROM classes cl2
          JOIN courses c2
            ON c2.id = cl2.course
          WHERE cl2.room = r.id
          GROUP BY cl2.room, c2.semester
          HAVING COUNT(DISTINCT cl2.course) >= 15
             AND COUNT(DISTINCT cl2.ctype) >= 4
      )
GROUP BY r.id
;

-- Q6:
CREATE OR REPLACE VIEW Q6(staff_id, staff_name, unique_co_teachers) AS
-- 对每个 staff/course 组合，如果该 staff 在这门课上担任过 Course Convenor，
-- 则这门课不用于统计合作人数；剩余课程里统计 distinct co-teacher。
SELECT p.unswid AS staff_id,
       p.name AS staff_name,
       COUNT(DISTINCT c.co_staff) AS unique_co_teachers
FROM (
    SELECT DISTINCT cs.staff,
           cs2.staff AS co_staff
    FROM course_staff cs
    JOIN course_staff cs2
      ON cs2.course = cs.course
     AND cs2.staff <> cs.staff
    WHERE NOT EXISTS (
        SELECT 1
        FROM course_staff cs3
        JOIN staff_roles sr3
          ON sr3.id = cs3.role
        WHERE cs3.staff = cs.staff
          AND cs3.course = cs.course
          AND sr3.name = 'Course Convenor'
    )
) c
JOIN staff s
  ON s.id = c.staff
JOIN people p
  ON p.id = s.id
GROUP BY p.unswid, p.name
HAVING COUNT(DISTINCT c.co_staff) >= 30
;

-- Q7:
CREATE OR REPLACE FUNCTION Q7(prog_code character(4), start_year integer) RETURNS text AS $$
DECLARE
    chosen_program integer;
    cohort_size integer;
    retained_count integer;
    retained_pct numeric;
BEGIN
    -- 如果同一个 code 对应多个 program id，
    -- 取 program_enrolments 中最早 semester 最小的那个。
    SELECT program_id
    INTO chosen_program
    FROM (
        SELECT p.id AS program_id
        FROM programs p
        LEFT JOIN program_enrolments pe
          ON pe.program = p.id
        WHERE p.code = prog_code
        GROUP BY p.id
        ORDER BY MIN(pe.semester), p.id
        LIMIT 1
    ) chosen;

    IF chosen_program IS NULL THEN
        RETURN 'WARNING: Invalid Program or Cohort';
    END IF;

    -- cohort：第一次 enrol 在该 program 的年份正好等于 start_year 的学生
SELECT COUNT(*)::integer,
           COUNT(
               CASE
                   WHEN EXISTS (
                       SELECT 1
                       FROM program_enrolments pe2
                       JOIN semesters se2
                         ON se2.id = pe2.semester
                       WHERE pe2.program = chosen_program
                         AND pe2.student = cohort.student
                         AND se2.year = start_year + 2
                   )
                   THEN 1
               END
           )::integer
    INTO cohort_size, retained_count
    FROM (
        SELECT pe.student
        FROM program_enrolments pe
        JOIN semesters se
          ON se.id = pe.semester
        WHERE pe.program = chosen_program
        GROUP BY pe.student
        HAVING MIN(se.year) = start_year
    ) cohort;

    IF COALESCE(cohort_size, 0) = 0 THEN
        RETURN 'WARNING: Invalid Program or Cohort';
    END IF;

    retained_pct := ROUND(retained_count * 100.0 / cohort_size, 2);

    RETURN 'Cohort size: ' || cohort_size
        || ', Retained after 2 years: '
        || TO_CHAR(retained_pct, 'FM999999990.00') || '%';
END;
$$ language plpgsql;

-- Q8:
CREATE OR REPLACE FUNCTION Q8(unswid integer, target_year integer, target_term character(2)) RETURNS text AS $$
DECLARE
    student_id_found integer;
    wanted_semester integer;
    current_wam numeric;
    current_attempted integer;
    current_passed integer;
    previous_semester integer;
    previous_wam numeric;
    previous_attempted integer;
    previous_passed integer;
    current_bad_standing boolean;
    previous_bad_standing boolean;
BEGIN
    -- 先把外部学号转成内部 student id
    SELECT s.id
    INTO student_id_found
    FROM students s
    JOIN people p
      ON p.id = s.id
    WHERE p.unswid = Q8.unswid;

    IF student_id_found IS NULL THEN
        RETURN 'No valid enrolments for term';
    END IF;

    -- 如果同一个 (year, term) 对应多个 semester，取 id 最小的那个
    SELECT MIN(se.id)
    INTO wanted_semester
    FROM semesters se
    WHERE se.year = target_year
      AND se.term = target_term;

    IF wanted_semester IS NULL THEN
        RETURN 'No valid enrolments for term';
    END IF;

    -- 统计目标学期：term WAM、attempted UOC、passed UOC
    SELECT ROUND(COALESCE(SUM(ce.mark * su.uoc)::numeric / NULLIF(SUM(su.uoc), 0), 0), 2),
           COALESCE(SUM(su.uoc), 0),
           COALESCE(SUM(CASE WHEN ce.mark >= 50 THEN su.uoc ELSE 0 END), 0)
    INTO current_wam, current_attempted, current_passed
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    WHERE ce.student = student_id_found
      AND c.semester = wanted_semester
      AND ce.mark IS NOT NULL;

    IF COALESCE(current_attempted, 0) = 0 THEN
        RETURN 'No valid enrolments for term';
    END IF;

    -- 找到时间上紧挨着的前一个“有非空 mark 的 enrolled term”
    SELECT prev.semester_id
    INTO previous_semester
    FROM (
        SELECT DISTINCT se.id AS semester_id,
               se.starting
        FROM course_enrolments ce
        JOIN courses c
          ON c.id = ce.course
        JOIN semesters se
          ON se.id = c.semester
        JOIN semesters tgt
          ON tgt.id = wanted_semester
        WHERE ce.student = student_id_found
          AND ce.mark IS NOT NULL
          AND (
              se.starting < tgt.starting
              OR (se.starting = tgt.starting AND se.id < tgt.id)
          )
        ORDER BY se.starting DESC, se.id DESC
        LIMIT 1
    ) prev;

    IF previous_semester IS NOT NULL THEN
        SELECT ROUND(COALESCE(SUM(ce.mark * su.uoc)::numeric / NULLIF(SUM(su.uoc), 0), 0), 2),
               COALESCE(SUM(su.uoc), 0),
               COALESCE(SUM(CASE WHEN ce.mark >= 50 THEN su.uoc ELSE 0 END), 0)
        INTO previous_wam, previous_attempted, previous_passed
        FROM course_enrolments ce
        JOIN courses c
          ON c.id = ce.course
        JOIN subjects su
          ON su.id = c.subject
        WHERE ce.student = student_id_found
          AND c.semester = previous_semester
          AND ce.mark IS NOT NULL;
    END IF;

    -- 当前 term 只要 WAM < 50 或通过 UOC 不足一半，就算 probation
    current_bad_standing := (
        current_wam < 50
        OR current_passed < current_attempted / 2.0
    );
    previous_bad_standing := (
        COALESCE(previous_attempted, 0) > 0
        AND (
            previous_wam < 50
            OR previous_passed < previous_attempted / 2.0
        )
    );

    IF current_bad_standing AND previous_bad_standing THEN
        RETURN 'Suspension';
    ELSIF current_bad_standing THEN
        RETURN 'Probation';
    ELSE
        RETURN 'Good Standing';
    END IF;
END;
$$ language plpgsql;

-- Q9
CREATE OR REPLACE FUNCTION Q9(unswid integer) RETURNS text AS $$
DECLARE
    sid integer;
    stream_code_found character(6);
    major_prefix text;
    overall_wam numeric;
    major_wam numeric;
    wam_gap numeric;
    gap_text text;
BEGIN
    -- 先根据 unswid 找内部 student id
    SELECT s.id
    INTO sid
    FROM students s
    JOIN people p
      ON p.id = s.id
    WHERE p.unswid = Q9.unswid;

    IF sid IS NULL THEN
        RETURN 'WARNING: Invalid Student Input';
    END IF;

    -- 如果有多个 stream enrolment，题目要求选择 stream id 最小的那个
    SELECT st.code
    INTO stream_code_found
    FROM program_enrolments pe
    JOIN stream_enrolments se
      ON se.partof = pe.id
    JOIN streams st
      ON st.id = se.stream
    WHERE pe.student = sid
    ORDER BY st.id
    LIMIT 1;

    major_prefix := SUBSTRING(stream_code_found FROM 1 FOR 4);

    -- Overall WAM：所有有效课程
    SELECT ROUND(COALESCE(SUM(ce.mark * su.uoc)::numeric / NULLIF(SUM(su.uoc), 0), 0), 2)
    INTO overall_wam
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    WHERE ce.student = sid
      AND ce.mark IS NOT NULL
      AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE');

    -- Major WAM：只保留 subject code 前缀和 stream 前 4 位一致的课程
    SELECT ROUND(
               COALESCE(
                   SUM(ce.mark * su.uoc)::numeric / NULLIF(SUM(su.uoc), 0),
                   0
               ),
               2
           )
    INTO major_wam
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    WHERE ce.student = sid
      AND ce.mark IS NOT NULL
      AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
      AND major_prefix IS NOT NULL
      AND su.code LIKE major_prefix || '%';

    overall_wam := COALESCE(overall_wam, 0);
    major_wam := COALESCE(major_wam, 0);
    wam_gap := ROUND(major_wam - overall_wam, 2);

    -- 差值为正时题目要求显式打印 +
    IF wam_gap > 0 THEN
        gap_text := TO_CHAR(wam_gap, 'FM+999999990.00');
    ELSE
        gap_text := TO_CHAR(wam_gap, 'FM999999990.00');
    END IF;

    RETURN 'Overall WAM: ' || TO_CHAR(overall_wam, 'FM999999990.00')
        || ', Major WAM: ' || TO_CHAR(major_wam, 'FM999999990.00')
        || ', Difference: ' || gap_text;
END;
$$ language plpgsql;


-- Q10
CREATE OR REPLACE FUNCTION Q10(unswid integer) RETURNS SETOF text AS $$
DECLARE
    student_id_found integer;
    term_row record;
    enrolment_row record;
    term_wam numeric;
    term_uoc_passed integer;
    cumulative_wam numeric;
    cumulative_uoc integer;
BEGIN
    -- 先根据外部学号找到内部 student id
    SELECT s.id
    INTO student_id_found
    FROM students s
    JOIN people p
      ON p.id = s.id
    WHERE p.unswid = Q10.unswid;

    IF student_id_found IS NULL THEN
        RETURN NEXT 'WARNING: Invalid Student Input';
        RETURN;
    END IF;

    -- 按 semester 开始时间顺序遍历学生所有有 enrolment 的学期
    FOR term_row IN
        SELECT DISTINCT se.id,
               se.year,
               se.term,
               se.starting
        FROM course_enrolments ce
        JOIN courses c
          ON c.id = ce.course
        JOIN semesters se
          ON se.id = c.semester
        WHERE ce.student = student_id_found
        ORDER BY se.starting, se.id
    LOOP
        -- 学期标题行
        RETURN NEXT '--- ' || term_row.year || ' ' || term_row.term || ' ---';

        -- 当前学期的课程按 subject code 排序逐行输出
        FOR enrolment_row IN
            SELECT BTRIM(su.code) AS subject_code,
                   ce.mark,
                   ce.grade::text AS grade_text
            FROM course_enrolments ce
            JOIN courses c
              ON c.id = ce.course
            JOIN subjects su
              ON su.id = c.subject
            WHERE ce.student = student_id_found
              AND c.semester = term_row.id
            ORDER BY su.code
        LOOP
            -- mark 为 NULL 时严格按题目要求输出 N/A
            IF enrolment_row.mark IS NULL THEN
                RETURN NEXT enrolment_row.subject_code || ' - N/A (N/A)';
            ELSE
                RETURN NEXT enrolment_row.subject_code || ' - ' || enrolment_row.mark
                    || ' (' || COALESCE(enrolment_row.grade_text, 'N/A') || ')';
            END IF;
        END LOOP;

        -- 计算当前学期：
        -- 1. term WAM：只统计 mark 非空且 grade 可计入 WAM 的课程
        -- 2. passed UOC：所有 mark >= 50 的课程 UOC，总和不看 grade
        SELECT ROUND(
                   COALESCE(
                       SUM(
                           CASE
                               WHEN ce.mark IS NOT NULL
                                AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
                               THEN ce.mark * su.uoc
                           END
                       )::numeric
                       / NULLIF(
                           SUM(
                               CASE
                                   WHEN ce.mark IS NOT NULL
                                    AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
                                   THEN su.uoc
                               END
                           ),
                           0
                       ),
                       0
                   ),
                   2
               ),
               COALESCE(SUM(CASE WHEN ce.mark >= 50 THEN su.uoc ELSE 0 END), 0)
        INTO term_wam, term_uoc_passed
        FROM course_enrolments ce
        JOIN courses c
          ON c.id = ce.course
        JOIN subjects su
          ON su.id = c.subject
        WHERE ce.student = student_id_found
          AND c.semester = term_row.id;

        -- 输出当前学期 summary
        RETURN NEXT 'Term WAM: ' || TO_CHAR(COALESCE(term_wam, 0), 'FM999999990.00')
            || ' | Term UOC Passed: ' || COALESCE(term_uoc_passed, 0);
    END LOOP;

    -- 最后计算整个学生历史上的 cumulative WAM 和 TOTAL UOC
    SELECT ROUND(
               COALESCE(
                   SUM(
                       CASE
                           WHEN ce.mark IS NOT NULL
                            AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
                           THEN ce.mark * su.uoc
                       END
                   )::numeric
                   / NULLIF(
                       SUM(
                           CASE
                               WHEN ce.mark IS NOT NULL
                                AND COALESCE(ce.grade::text, '') NOT IN ('SY', 'XE', 'T', 'PE')
                               THEN su.uoc
                           END
                       ),
                       0
                   ),
                   0
               ),
               2
           ),
           COALESCE(SUM(CASE WHEN ce.mark >= 50 THEN su.uoc ELSE 0 END), 0)
    INTO cumulative_wam, cumulative_uoc
    FROM course_enrolments ce
    JOIN courses c
      ON c.id = ce.course
    JOIN subjects su
      ON su.id = c.subject
    WHERE ce.student = student_id_found;

    -- 输出最后一行 cumulative summary
    RETURN NEXT '=== CUMULATIVE WAM: '
        || TO_CHAR(COALESCE(cumulative_wam, 0), 'FM999999990.00')
        || ' | TOTAL UOC: ' || COALESCE(cumulative_uoc, 0) || ' ===';
    RETURN;
END;
$$ language plpgsql;
