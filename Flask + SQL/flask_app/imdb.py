from flask import Flask, jsonify, abort, make_response, render_template, request
import psycopg2
from configparser import ConfigParser

def filter_muvie_id(val,
                    filter_name = 'tconst',
                    limit_str = 10,
                    order_by = 'tconst',
                    user = "docker",
                    password = "docker",
                    host = "138.197.176.123",
                    port = "5430",
                    database = "imdb"
                   ):

    """
    производит поиск и возвращает идентификаторы фильмов, отвечающий условиям поиска в
    базе данных imdb.
    параметры:
            val - значение переменной для поиска по колонке column,
            filter_name - название колонки в таблице basics, по которой производится
                        фильтрация, значение по умолчанию 'tconst', возможные значения:
                        tconst, titletype, primarytitle, originaltitle, isadult, startyear,
                        endyear, runtimeminutes, genres
            limit_str - ограничение количества выдачи. по умолчанию -  10,
            order_by - название колонки в таблице basics, по которой производится
                        сортировка, значение по умолчанию   'tconst'
            user - учетная запись для подключения БД, значение по умолчанию"docker",
            password - пароль учетной записи, значение по умолчанию "docker",
            host = ip адрес сервера, на котором расположена БД,
                    значение по умолчанию "138.197.176.123",
            port - порт подключения к БД, значение по умолчанию "5430",
            database - название БД, значение по умолчанию "imdb"
    Возвращает  json форматированную строку вида {"movies": ["tt0000001", "tt0453643"]}
    в случае успешного поиска.
    В случае ошибки или отсутствия идентификаторов фильмов, удовлетворяющих
    условиям - возвращает  None

    """
    try:
        connection = psycopg2.connect(user = user,
                                      password = password ,
                                      host = host,
                                      port = port,
                                      database = database)
        cursor = connection.cursor()

        filter_str = f" where b.{filter_name} = '{val}'"
        order_str = f" order by {order_by}"
        limit = f" limit {limit_str}"
        query = ("select b.tconst from imdb.basics b " 
                 + filter_str + order_str + limit + ";")
    
        cursor.execute(query)
        colnames = [desc[0] for desc in cursor.description]
        rows = [row[0] for row in cursor.fetchall()]
        if len(rows) == 0 :
            if(connection):
                cursor.close()
                connection.close()
            return make_response('', 404)
        else:
            if(connection):
                cursor.close()
                connection.close()
            return make_response(jsonify(movies=rows
                                        ), 200)
        

    except (Exception, psycopg2.Error) as error :
        return make_response('', 404)

def top_k(id_list,
          full_id_list,
          top_n,
          user = "docker",
          password = "docker",
          host = "138.197.176.123",
          port = "5430",
          database = "imdb"
         ):
    """
    производит  наиболее подходящих фильмов для пользователя, возвращает top_n
    идентификаторов  фильмов, отвечающий условиям поиска в базе данных imdb.
    Для идентификаторов фильмов id_list находятся значения из средних рейтингов из таблицы
    ratings. По максимальному значению из этих рейтингов производится фильтрация в таблице
    ratings (с округлением до второго знака). Из найденного списка удаляются записи с идентификаторами из
    списка full_id_list после чего производится сортировка по количеству голосов.
    Из отсортированного списка  оставляются top_n значений.
    параметры:
            id_list - список наиболее понравившихся фильмов из запроса (с одинаковым максимальным
            коеффикиентом),
            full_id_list - полный список идентификаторов фильмов из запроса,
            user - учетная запись для подключения БД, значение по умолчанию"docker",
            password - пароль учетной записи, значение по умолчанию "docker",
            host = ip адрес сервера, на котором расположена БД,
                    значение по умолчанию "138.197.176.123",
            port - порт подключения к БД, значение по умолчанию "5430",
            database - название БД, значение по умолчанию "imdb"
    Возвращает make_response с json форматированной строкой вида
    {"ratings": ["tt0000001", "tt0453643"]} и http идентификатором 200
    в случае успешного поиска.
    В случае ошибки или отсутствия идентификаторов фильмов, удовлетворяющих
    условиям - возвращает  пустое значение и http идентификатор 404
    """
    str_ids = "' , '".join(id_list)
    str_ids = "'" + str_ids + "'"
    str_full_ids = "' , '".join(full_id_list)
    str_full_ids = "'" + str_full_ids + "'"
    print(str_full_ids)

    try:
        connection = psycopg2.connect(user = user,
                                      password = password ,
                                      host = host,
                                      port = port,
                                      database = database)
        cursor = connection.cursor()

        query = f"SELECT r.tconst \
                FROM imdb.ratings r \
                WHERE ROUND(CAST(r.averagerating AS numeric), 2) IN ( \
                SELECT ROUND(CAST(MAX(rs.averagerating) AS numeric), 2) AS max_rating \
                FROM imdb.ratings rs WHERE  rs.tconst IN ({str_ids}) \
                ) AND r.tconst  NOT IN ({str_full_ids}) \
                ORDER BY r.numvotes DESC \
                LIMIT {top_n};"

    
        cursor.execute(query)

        rows = [row[0] for row in cursor.fetchall()]

        if len(rows) == 0 :
            if(connection):
                cursor.close()
                connection.close()
            return make_response('', 404)
        else:
            if(connection):
                cursor.close()
                connection.close()
            return make_response(jsonify(ratings=rows), 200)
        

    except (Exception, psycopg2.Error) as error :
        return make_response('', 404)
        

    except (Exception, psycopg2.Error) as error :
        return make_response('', 404)


def db_request(req, column, default = True):
    """
    оболочка для работы с filter_muvie_id либо со значениями параметров подключения
    из файла config.ini либо со значениями по умолчанию.
    Дополнительно извлекается ограничитель количества идентификаторов из строки запрос ( если присутствует)
    вход:
            req - строка запроса,
            column - колонка для фильтрации,
            default - выбор параметров подключения, значение по умолчанию True
    """    
    req = req.split('&lim=')
    if len(req) > 1:
        len_lim = req[-1]
    elif default:
        len_lim = 10
    else:
        len_lim = DB_CONFIG["limit_str"]
    print(req, len_lim, column)
    if default:
        return filter_muvie_id(val = req[0], 
                               filter_name  = column, 
                               limit_str = len_lim
                              )    
    else:
        return filter_muvie_id(val = req[0], 
                               filter_name  = column, 
                               limit_str = len_lim,
                               order_by = DB_CONFIG["order_by"],
                               user = SERVERCONFIG["user"],
                               password = SERVERCONFIG["password"],
                               host = SERVERCONFIG["host"],
                               port = SERVERCONFIG["port"],
                               database = SERVERCONFIG["database"]
                              )


app = Flask(__name__)

# app name 
@app.errorhandler(404) 
  
# inbuilt function which takes error as parameter 
def not_found(e): 
  
# defining function 
  return render_template("404.html") , 404



@app.route('/suggest/<top_n>' ,methods = ['GET', 'POST'])
def suggest(top_n=None):
    req_json = request.get_json(force=True) 
    full_ids = list(req_json["likes"].keys())
    ids = [key for key, value in req_json["likes"].items() if value == max(req_json["likes"].values())]
    return top_k(ids, full_ids , top_n)


@app.route('/tconst/<req>',methods = ['GET'])
def tconst(req=None):
    return db_request(req, 'tconst', default_value)
# filter_muvie_id(val = req[0], limit_str = len_lim)


@app.route('/titletype/<req>',methods = ['GET'])
def titletype(req=None):
    return db_request(req, 'titletype', default_value)


@app.route('/primarytitle/<req>',methods = ['GET'])
def primarytitle(req=None):
    return db_request(req, 'primarytitle', default_value)

@app.route('/originaltitle/<req>',methods = ['GET'])
def originaltitle(req=None):
    return db_request(req, 'originaltitle', default_value)


@app.route('/isadult/<req>',methods = ['GET'])
def isadult(req=None):
    return db_request(req, 'isadult', default_value)


@app.route('/startyear/<req>',methods = ['GET'])
def startyear(req=None):
    return db_request(req, 'startyear', default_value)


@app.route('/endyear/<req>')
def endyear(req=None):
    return db_request(req, 'endyear', default_value)


@app.route('/runtimeminutes/<req>',methods = ['GET'])
def runtimeminutes(req=None):
    return db_request(req, 'runtimeminutes', default_value)


@app.route('/genres/<req>' ,methods = ['GET'])
def genres(req=None):
    return db_request(req, 'genres', default_value) 

if __name__ == '__main__':
    print('staring app...')
    try:
        config_object = ConfigParser()
        config_object.read("config.ini")
        DB_CONFIG = config_object["DB_CONFIG"]
        SERVERCONFIG = config_object["SERVERCONFIG"]
        default_value = False
    except:
        default_value = True
        print("error with config.ini. Programm will start with default config")
    app.run(host ='0.0.0.0', port = 5000)

