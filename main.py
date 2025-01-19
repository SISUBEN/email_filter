from email_filter import EmailFilterFSM

filter = EmailFilterFSM()

print(filter.do_filter("test@gmail.com"))

