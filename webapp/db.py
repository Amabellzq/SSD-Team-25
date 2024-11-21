# import pymysql
# from flask import current_app


# def get_db_connection():
#     try:
#         return pymysql.connect(
#             host=current_app.config["MYSQL_HOST"],
#             port=int(current_app.config["MYSQL_PORT"]),
#             user=current_app.config["MYSQL_ADMIN_USER"],
#             password=current_app.config["MYSQL_ADMIN_PASSWORD"],
#             database=current_app.config["MYSQL_DATABASE"],
#             cursorclass=pymysql.cursors.DictCursor
#         )
#     except KeyError as e:
#         raise ValueError(f"Missing configuration for {str(e)}")
#     except pymysql.MySQLError as e:
#         raise ValueError(f"Database connection error: {str(e)}")
