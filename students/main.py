import sqlite3
import pandas as pd

conn = sqlite3.connect('baza.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS уровень_обучения (
    id_уровня INTEGER PRIMARY KEY,
    название VARCHAR(50) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS направления (
    id_направления INTEGER PRIMARY KEY,
    название VARCHAR(100) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS типы_обучения (
    id_типа INTEGER PRIMARY KEY,
    название VARCHAR(50) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS студенты (
    id_студента INTEGER PRIMARY KEY,
    id_уровня INTEGER NOT NULL,
    id_направления INTEGER NOT NULL,
    id_типа_обучения INTEGER NOT NULL,
    фамилия VARCHAR(50) NOT NULL,
    имя VARCHAR(50) NOT NULL,
    отчество VARCHAR(50),
    средний_балл DECIMAL(3,2),
    FOREIGN KEY (id_уровня) REFERENCES уровень_обучения(id_уровня),
    FOREIGN KEY (id_направления) REFERENCES направления(id_направления),
    FOREIGN KEY (id_типа_обучения) REFERENCES типы_обучения(id_типа)
)
''')

df_level = pd.read_csv('level.csv', sep=';', encoding='utf-8')
df_level.to_sql('уровень_обучения', conn, if_exists='replace', index=False)
    

df_speciality = pd.read_csv('speciality.csv', sep=';', encoding='utf-8')
df_speciality.to_sql('направления', conn, if_exists='replace', index=False)
    
df_type = pd.read_csv('type_study.csv', sep=';', encoding='utf-8')

df_type.columns = ['id_типа', 'название']
df_type.to_sql('типы_обучения', conn, if_exists='replace', index=False)
    
df_main = pd.read_csv('main.csv', sep=';', encoding='utf-8')
df_main = df_main.dropna(subset=['id_студента'], how='all')
df_main = df_main[df_main['id_студента'].notna()]
    
df_main['средний_балл'] = df_main['средний_балл'].astype(str).str.replace(',', '.').astype(float)
df_main.to_sql('студенты', conn, if_exists='replace', index=False)

cursor.execute('SELECT COUNT(*) FROM студенты')
count_students = cursor.fetchone()[0]
print(f"Количество студентов: {count_students}")

cursor.execute('SELECT н.название, COUNT(*) as количество FROM студенты с JOIN направления н ON с.id_направления = н.id_направления GROUP BY н.название')
print(cursor.fetchall())

cursor.execute('SELECT т.название, COUNT(*) as количество FROM студенты с JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа GROUP BY т.название')
print(cursor.fetchall())

cursor.execute('SELECT н.название, MAX(средний_балл) as количество FROM студенты с JOIN направления н ON с.id_направления = н.id_направления GROUP BY н.название')
print(cursor.fetchall())

cursor.execute('SELECT н.название, MIN(средний_балл) as количество FROM студенты с JOIN направления н ON с.id_направления = н.id_направления GROUP BY н.название')
print(cursor.fetchall())

cursor.execute('SELECT н.название, AVG(средний_балл) as количество FROM студенты с JOIN направления н ON с.id_направления = н.id_направления GROUP BY н.название')
print(cursor.fetchall())

cursor.execute('SELECT т.название, AVG(средний_балл) as количество FROM студенты с JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа GROUP BY т.название')
print(cursor.fetchall())

cursor.execute('SELECT у.названия, AVG(средний_балл) as количество FROM студенты с JOIN уровень_обучения у ON с.id_уровня = у.id_уровня GROUP BY у.названия')
print(cursor.fetchall())

cursor.execute('''SELECT с.фамилия, с.имя, с.отчество, с.средний_балл 
               FROM студенты с 
               JOIN направления н ON с.id_направления = н.id_направления 
               JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа 
               WHERE н.название = 'РПО' AND т.название = 'Очное' 
               ORDER BY с.средний_балл DESC LIMIT 5''')
print(cursor.fetchall())

cursor.execute('''
    SELECT фамилия, COUNT(*) as количество
    FROM студенты
    GROUP BY фамилия
    HAVING COUNT(*) > 1
    ORDER BY количество DESC
''')
print(cursor.fetchall())

cursor.execute('''
    SELECT фамилия, имя, отчество, COUNT(*) as количество
    FROM студенты
    GROUP BY фамилия, имя, отчество
    HAVING COUNT(*) > 1
    ORDER BY количество DESC
''')
print(cursor.fetchall())