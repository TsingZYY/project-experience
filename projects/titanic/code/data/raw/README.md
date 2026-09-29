# 自行提供的数据

本代码包不分发原始数据。请按[Kaggle Titanic数据页](https://www.kaggle.com/competitions/titanic/data)的要求自行取得：

- train.csv：891行，包含Survived标签。
- test.csv：418行，不包含Survived标签。
- gender_submission.csv：提交格式示例，不是真实测试标签。

将三份文件放在本目录，或设置TITANIC_DATA_DIR到相应目录。输入字段包括PassengerId、Pclass、Name、Sex、Age、SibSp、Parch、Ticket、Fare、Cabin、Embarked。

Notebook先检查结构、ID及目标值，再运行分析。用户提供的数据是否具有合适使用权限由其来源决定；本包不授予第三方数据的额外许可。

