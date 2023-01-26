import MySQLdb

try:
    db = MySQLdb.connect(host="misfinanzasapp.mysql.pythonanywhere-services.com",    # your host, usually localhost
                     user="misfinanzasapp",         # your username
                     passwd="S1st3m4s",  # your password
                     db="misfinanzasapp$default")        # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    # Use all the SQL you like
    cur.execute("CALL proc_Programador();")

    db.close()

except Exception as e:
    print(e)