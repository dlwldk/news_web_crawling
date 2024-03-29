import psycopg2
conn = psycopg2.connect(host='localhost', dbname='postgres', user='아이디', password='비밀번호', port=5432)
cur = conn.cursor()

cur.execute("CREATE TYPE categories AS ENUM ('society', 'politics', 'economic', 'culture', 'digital', 'etc');") # category 만들기
cur.execute("CREATE TABLE News_list (news_date date, serial_num bigint, link text not null, constraint list_pkey primary key (news_date, serial_num));")
cur.execute("CREATE TABLE News (news_date date, serial_num bigint, title text not null, input_date text not null, subtitle text, press_agency varchar(10) not null, constraint news_pkey primary key (news_date, serial_num), constraint news_list_serial_num_fkey foreign key(news_date, serial_num) references News_list (news_date, serial_num) on delete cascade on update cascade);")
cur.execute("CREATE TABLE News_Category (news_date date, serial_num bigint, category categories not null, keyword text not null, keyword_count smallint not null, constraint category_pkey primary key (news_date, serial_num, keyword), constraint category_list_serial_num_fkey foreign key(news_date, serial_num) references News_list (news_date, serial_num) on delete cascade on update cascade);")

conn.commit()
cur.close()
conn.close()
