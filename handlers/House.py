# -*- coding:utf-8 -*-

from .BaseHandler import BaseHandler
from utils.response_code import RET
import logging
import json
import constants
import math

from utils.commons import required_login


class AreaInfoHandler(BaseHandler):
    """获取区域信息"""

    def get(self):
        # 先查redis
        try:
            res = self.redis.get("area_info")
            # res = json.loads(res)
        except Exception as e:
            res = None
            logging.error(e)
        if res:
            # return self.write(dict(errcode=RET.OK, errmsg="ok!!", data=res))
            return self.write("{'errcode':%s,errmsg:%s,data:%s}" % (RET.OK, "ok!!!", res))  # 少一次序列化操作
        print(res)
        logging.debug(res)
        # 继续执行查询数据库
        try:
            ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询出错了!!"))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="no data"))
        areas = []
        for x in ret:
            model = {
                "area_id": x["ai_area_id"],
                "name": x["ai_name"],
            }
            areas.append(model)
        # 存储到redis
        try:
            self.redis.setex("area_info", constants.REDIS_AREA_INFO_EXPIRES_SECONDES, json.dumps(areas))
        except Exception as e:
            logging.error(e)

        self.write(dict(errcode=RET.OK, errmsg="ok!!", data=areas))


class MyHousehandler(BaseHandler):

    @required_login
    def get(self):
        """user_id从session获取而不是前端穿过来更加安全"""
        # 这里能使用self.session 的原因是 @required_login装饰器调用了get_current_user()方法
        # 而且get_current_user方法里面动态的添加了属性给BaseHandler()
        user_id = self.session.data["user_id"]
        try:
            sql = "select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url " \
                  "from ih_house_info a inner join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s;"
            ret = self.db.query(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询出错了!!"))
        houses = []
        if ret:
            for line in ret:
                house = {
                    "house_id": line["hi_house_id"],
                    "title": line["hi_title"],
                    "price": line["hi_price"],
                    "ctime": line["hi_ctime"].strftime("%Y-%m-%d"),  # 时间转为字符串
                    "area_name": line["ai_name"],
                    "img_url": constants.QINIU_URL_PREFIX + line["hi_index_image_url"] if line[
                        "hi_index_image_url"] else ""
                }
                houses.append(house)
        house_test = {
            "house_id": "测试",
            "title": "测试title",
            "price": 998,
            "ctime": '2018-03-21',  # 时间转为字符串
            "area_name": '北京',
            "img_url": 'http://p5ufc44c8.bkt.clouddn.com/FlsI6fRX-RJ_FFF39hgGT0zb_zlp'
        }
        houses.append(house_test)
        self.write(dict(errcode=RET.OK, errmsg="ok", houses=houses))


class HouseInfoHandler(BaseHandler):
    def get(self):
        """拉取房源信息"""
        self.write("ok")

    @required_login
    def post(self):
        """新增房源信息
        方便测试
        注释登陆装饰器和xsrf校验

        """
        user_id = self.session.data["user_id"]
        # 测试
        # user_id = 11
        title = self.json_args.get("title")
        price = self.json_args.get("price")
        area_id = self.json_args.get("area_id")
        address = self.json_args.get("address")
        room_count = self.json_args.get("room_count")
        acreage = self.json_args.get("acreage")
        unit = self.json_args.get("unit")
        capacity = self.json_args.get("capacity")
        beds = self.json_args.get("beds")
        deposit = self.json_args.get("deposit")
        min_days = self.json_args.get("min_days")
        max_days = self.json_args.get("max_days")
        facility = self.json_args.get("facility")  # 对一个房屋的设施，是列表类型
        # 校验
        if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days,
                    max_days)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg="缺少参数"))
        try:
            price = int(price) * 100
            deposit = int(deposit) * 100
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="参数错误"))
        # 存储ih_house_info 基本表
        try:
            sql = "insert into ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count," \
                  "hi_acreage,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days)" \
                  "values(%(user_id)s,%(title)s,%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(acreage)s," \
                  "%(house_unit)s,%(capacity)s,%(beds)s,%(deposit)s,%(min_days)s,%(max_days)s)"
            # ret = self.db.execute_rowcount()
            house_id = self.db.execute(sql, user_id=user_id, title=title, price=price, area_id=area_id, address=address,
                                       room_count=room_count, acreage=acreage, house_unit=unit, capacity=capacity,
                                       beds=beds, deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="数据错误!"))

        # 存储配套设置
        try:
            sql = "insert into ih_house_facility(hf_house_id,hf_facility_id) values"
            sql_tuple = []  # 临时列表容器
            temp = []  # 最后转换为元祖
            for facility_id in facility:
                sql_tuple.append("(%s,%s)")  # 2.存到列表里
                # sql += "(%s,%s),"
                temp.append(house_id)  # 元素添加
                temp.append(facility_id)
            # sql = sql[:-1]
            # 2.存到列表里取出来拼接sql
            sql += ",".join(sql_tuple)
            logging.debug(sql)
            temp = tuple(temp)  # 最后转换为元祖 元祖解包

            new_id = self.db.execute(sql, *temp)  # 元祖解包
        except Exception as e:
            logging.error(e)
            try:
                # torndb 没有提供事务机制所以必须手动删除
                self.db.execute("delete from ih_house_info WHERE  hi_house_id=%s", house_id)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errcode=RET.DBERR, errmsg="删除出错"))
            else:
                return self.write(dict(errcode=RET.DBERR, errmsg="存储房屋基本信息失败!!"))

        self.write(dict(errcode=RET.OK, errmsg="OK", house_id=house_id))


class HouseListHandler(BaseHandler):
    def get(self):
        """
        get 方式 对数据本身不会有什么影响不存在安全问题
                传入参数说明
                start_date 用户查询的起始时间 sd     非必传   ""          "2017-02-28"
                end_date    用户查询的终止时间 ed    非必传   ""
                area_id     用户查询的区域条件   aid 非必传   ""
                sort_key    排序的关键词     sk     非必传   "new"      "new" "booking" "price-inc"  "price-des"
                page        返回的数据页数     p     非必传   1
        """
        start_date = self.get_argument("sd", "")  # 不设置默认值会报400
        end_date = self.get_argument("ed", "")
        area_id = self.get_argument("aid", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")
        # 校验参数

        # 数据查询
        # 涉及到表： ih_house_info 房屋的基本信息  ih_user_profile 房东的用户信息 ih_order_info 房屋订单数据

        sql = "select * from ih_house_info AS ihi INNER JOIN  ih_user_profile AS iup ON ihi.hi_user_id=iup.up_user_id" \
              "left JOIN ih_order_info AS ioi ON ioi.oi_house_id = ihi.hi_house_id "
        """出现在order by 后面的必须出现在distinct 里面
        房屋基本信息都一样只要distinct 后面不要出现start_date end_date 就好,理解为联合去重
        """
        sql = "select distinct hi_title,hi_house_id,hi_price,hi_room_count,hi_address,hi_order_count,up_avatar,hi_index_image_url,hi_ctime" \
              " from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id left join ih_order_info" \
              " on hi_house_id=oi_house_id"
        sql_total_count = "select count(distinct hi_house_id) count from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id " \
                          "left join ih_order_info on hi_house_id=oi_house_id"
        sql_where = []  # 存储where 后面的条件语句容器
        sql_params = {}  # 存储参数
        if start_date and end_date:
            # sql_where.append("(not (oi_begin_date<%(end_date)s and oi_end_date>%(start_date)s))")
            sql_where.append(
                "((oi_begin_date>%(end_date)s or oi_end_date<%(start_date)s)) or (oi_begin_date is null and oi_end_date is null)")
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_where.append("oi_end_date<%(start_date)s")
            sql_params["start_date"] = start_date
        elif end_date:
            sql_where.append("oi_begin_date>%(end_date)s")
            sql_params["end_date"] = end_date
        if area_id:
            sql_where.append("hi_area_id=%(area_id)s")
            sql_params["area_id"] = area_id
        if sql_where:
            sql += " where "
            sql += " and ".join(sql_where)
            sql_total_count += " where "
            sql += " and ".join(sql_where)

        # 排序
        if "new" == sort_key:  # 按最新上传时间排序
            sql += " order by hi_ctime desc"
        elif "booking" == sort_key:  # 最受欢迎
            sql += " order by hi_order_count desc"
        elif "price-inc" == sort_key:  # 价格由低到高
            sql += " order by hi_price asc"
        elif "price-des" == sort_key:  # 价格由高到低
            sql += " order by hi_price desc"

        # 有了查询条件开始查询数据库
        try:
            # 先查询总条数
            ret = self.db.get(sql_total_count, **sql_params) # 类似字典的
        except Exception as e:
            logging.error(e)
            total_page = -1
        else:
            total_page = int(math.ceil(ret["count"] / float(constants.HOUSE_LIST_PAGE_CAPACITY)))
            page = int(page)
            if page > total_page:
                return self.write(dict(errcode=RET.OK, errmsg="OK", data=[], total_page=total_page))
        # 分页
        if 1 == page:
            sql += " limit %s" % constants.HOUSE_LIST_PAGE_CAPACITY
        else:
            sql += " limit %s,%s" % (
                # limit (page_Index -1)*pagesize, pagesize
                (page - 1) * constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY)
        logging.debug(sql)
        try:
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询出错"))
        data = []
        if ret:
            for l in ret:
                house = dict(
                    house_id=l["hi_house_id"],
                    title=l["hi_title"],
                    price=l["hi_price"],
                    room_count=l["hi_room_count"],
                    address=l["hi_address"],
                    order_count=l["hi_order_count"],
                    avatar=constants.QINIU_URL_PREFIX + l["up_avatar"] if l.get("up_avatar") else "",
                    image_url=constants.QINIU_URL_PREFIX + l["hi_index_image_url"] if l.get(
                        "hi_index_image_url") else ""
                )
                data.append(house)
        self.write(dict(errcode=RET.OK, errmsg="OK", data=data, total_page=total_page))