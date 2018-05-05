import time
import MySQLdb as my
from random import randint
temp=70.00


while True: 
	db = my.connect(host="192.168.1.22",
	user="rpi",
	passwd="olpride",
	db="test"
	)

	offset_int = randint(-50,50)
	offset = offset_int / 100.0
	temp = temp + offset
 	#temp_string = "{0:.2f}".format(temp)
	cursor = db.cursor()
 
	sql = "insert into temperature VALUES(now(), '%s')" % (temp)

	number_of_rows = cursor.execute(sql)
	db.commit()   # you need to call commit() method to save 
		      # your changes to the database
 
	db.close()
	print offset
	print temp
	time.sleep(5)

