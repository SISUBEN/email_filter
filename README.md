# email_filter
--------
基于Python有限状态机的邮件过滤器

写着玩的，有点粪

E.g: aaa@gmail.com 是合法邮件地址，会输出aaa@gmail.com

aa..@gmail.com 是非法邮件地址，会被直接过滤掉，返回空字符串

目前还没做好一堆地址的处理和将三级域名邮箱过滤
