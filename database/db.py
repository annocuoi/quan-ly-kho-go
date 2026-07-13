import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config import DATABASE
from decimal import Decimal

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE,
    cursor_factory=RealDictCursor
)


# =========================
# KẾT NỐI DATABASE
# =========================

def get_connection():

    conn = connection_pool.getconn()
    conn.autocommit = False
    return conn


def close_connection(conn):

    connection_pool.putconn(conn)

def tao_database():

    conn = get_connection()
    cur = conn.cursor()

    # =========================
    # APP INFO
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_info(
            id INTEGER PRIMARY KEY,
            version INTEGER
        )
    """)

    cur.execute("""
        INSERT INTO app_info(id, version)
        VALUES(1,1)
        ON CONFLICT (id) DO NOTHING
    """)

    # =========================
    # LOẠI GỖ
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loai_go(

            id SERIAL PRIMARY KEY,

            ten VARCHAR(255) NOT NULL,

            kieu_tinh VARCHAR(20) NOT NULL DEFAULT 'M3',

            day DOUBLE PRECISION,

            rong DOUBLE PRECISION,

            dai DOUBLE PRECISION,

            hien_thi BOOLEAN DEFAULT TRUE

        )
    """)

    # =========================
    # KHÁCH HÀNG
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS khach_hang(

            id SERIAL PRIMARY KEY,

            ten VARCHAR(255) NOT NULL,

            dien_thoai VARCHAR(20),

            dia_chi TEXT

        )
    """)

    # =========================
    # PHIẾU NHẬP
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phieu_nhap(

            id SERIAL PRIMARY KEY,

            so_phieu INTEGER UNIQUE NOT NULL,

            ngay DATE,

            khach_hang_id INTEGER NOT NULL,

            tong_tien DOUBLE PRECISION NOT NULL DEFAULT 0,

            loai_nhap VARCHAR(20) NOT NULL DEFAULT 'TUOI',

            FOREIGN KEY(khach_hang_id)
            REFERENCES khach_hang(id)

        )
    """)

    # =========================
    # CHI TIẾT PHIẾU
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap(

            id SERIAL PRIMARY KEY,

            phieu_nhap_id INTEGER NOT NULL,

            loai_go_id INTEGER NOT NULL,

            so_thanh INTEGER,

            so_thanh_con_lai INTEGER,

            so_luong DOUBLE PRECISION NOT NULL,

            so_luong_con_lai DOUBLE PRECISION NOT NULL,

            don_gia DOUBLE PRECISION NOT NULL,

            thanh_tien DOUBLE PRECISION NOT NULL,

            trang_thai VARCHAR(20) NOT NULL DEFAULT 'TUOI',

            FOREIGN KEY(phieu_nhap_id)
                REFERENCES phieu_nhap(id)
                ON DELETE CASCADE,

            FOREIGN KEY(loai_go_id)
                REFERENCES loai_go(id)

        )
    """)

    # =========================
    # HẦM SẤY
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ham_say(

            id SERIAL PRIMARY KEY,

            chi_tiet_phieu_nhap_id INTEGER NOT NULL,

            so_ham INTEGER NOT NULL,

            so_luong DOUBLE PRECISION,

            so_thanh INTEGER,

            trang_thai VARCHAR(20) DEFAULT 'DANG_SAY',

            ngay_vao TIMESTAMP DEFAULT NOW(),

            ngay_ra TIMESTAMP,

            da_ra_ham BOOLEAN DEFAULT FALSE,

            FOREIGN KEY(chi_tiet_phieu_nhap_id)
                REFERENCES chi_tiet_phieu_nhap(id)
                ON DELETE CASCADE

        )
    """)

    # =========================
    # KHO KHÔ
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kho_kho(

            id SERIAL PRIMARY KEY,

            ham_say_id INTEGER NOT NULL UNIQUE,

            ngay_vao TIMESTAMP DEFAULT NOW(),

            FOREIGN KEY(ham_say_id)
                REFERENCES ham_say(id)
                ON DELETE CASCADE

        )
    """)

    # =========================
    # LỊCH SỬ HẦM SẤY
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lich_su_ham(

            id SERIAL PRIMARY KEY,

            ham_say_id INTEGER,

            chi_tiet_phieu_nhap_id INTEGER NOT NULL,

            so_ham INTEGER NOT NULL,

            hanh_dong VARCHAR(20) NOT NULL,

            loai_hang VARCHAR(20) NOT NULL,

            so_luong DOUBLE PRECISION,

            so_thanh INTEGER,

            ngay TIMESTAMP DEFAULT NOW(),

            FOREIGN KEY(ham_say_id)
                REFERENCES ham_say(id)
                ON DELETE SET NULL,

            FOREIGN KEY(chi_tiet_phieu_nhap_id)
                REFERENCES chi_tiet_phieu_nhap(id)
                ON DELETE CASCADE

        )
    """)

    # =========================
    # CÔNG NỢ
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cong_no(

            id SERIAL PRIMARY KEY,

            khach_hang_id INTEGER NOT NULL,

            ngay DATE NOT NULL,

            loai VARCHAR(30) NOT NULL,

            so_tien DOUBLE PRECISION NOT NULL,

            phieu_nhap_id INTEGER,

            ghi_chu TEXT,

            FOREIGN KEY(khach_hang_id)
                REFERENCES khach_hang(id)
                ON DELETE CASCADE,

            FOREIGN KEY(phieu_nhap_id)
                REFERENCES phieu_nhap(id)
                ON DELETE CASCADE

        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS thanh_toan(

            id SERIAL PRIMARY KEY,

            cong_no_id INTEGER NOT NULL,

            ngay DATE NOT NULL,

            so_tien DOUBLE PRECISION NOT NULL,

            ghi_chu TEXT,

            FOREIGN KEY(cong_no_id)
                REFERENCES cong_no(id)
                ON DELETE CASCADE

        )
    """)

    # =========================
    # PHÂN LOẠI GỖ
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phan_loai_go(

            id SERIAL PRIMARY KEY,

            ten VARCHAR(255) NOT NULL,

            hien_thi BOOLEAN DEFAULT TRUE

        )
    """)

    # =========================
    # KHO ĐÃ PHÂN LOẠI
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kho_phan_loai(

            id SERIAL PRIMARY KEY,

            kho_kho_id INTEGER,

            chi_tiet_phieu_nhap_id INTEGER NOT NULL,

            phan_loai_go_id INTEGER NOT NULL,

            day DOUBLE PRECISION,
            rong DOUBLE PRECISION,
            dai DOUBLE PRECISION,

            so_luong DOUBLE PRECISION,

            so_thanh INTEGER,

            ngay TIMESTAMP DEFAULT NOW(),

            FOREIGN KEY(kho_kho_id)
                REFERENCES kho_kho(id)
                ON DELETE CASCADE,

            FOREIGN KEY(chi_tiet_phieu_nhap_id)
                REFERENCES chi_tiet_phieu_nhap(id)
                ON DELETE CASCADE,

            FOREIGN KEY(phan_loai_go_id)
                REFERENCES phan_loai_go(id)

        )
    """)

    conn.commit()
    close_connection(conn)


def lay_ds_loai_go(
    ten_go=None,
    loai_go_id=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            id,
            ten,
            kieu_tinh,
            day,
            rong,
            dai
        FROM loai_go
        WHERE hien_thi = TRUE
    """

    params = []

    # Lọc theo tên gỗ
    if ten_go is not None:
        sql += " AND ten = %s"
        params.append(ten_go)

    # Lọc theo quy cách (id loại gỗ)
    if loai_go_id is not None:
        sql += " AND id = %s"
        params.append(loai_go_id)

    sql += """
        ORDER BY
            ten,
            day NULLS FIRST,
            rong NULLS FIRST,
            dai NULLS FIRST
    """

    cur.execute(sql, tuple(params))

    data = cur.fetchall()

    close_connection(conn)

    return data

def them_loai_go(ten, kieu_tinh, day, rong, dai):

    if kieu_tinh == "TRONG_LUONG":
        day = None
        rong = None
        dai = None
        
    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO loai_go(

            ten,

            kieu_tinh,

            day,

            rong,

            dai

        )

        VALUES(%s,%s,%s,%s,%s)
    """, ( ten, kieu_tinh, day, rong, dai))

    conn.commit()

    close_connection(conn)

def sua_loai_go(id,  ten, kieu_tinh, day, rong, dai):

    if kieu_tinh == "TRONG_LUONG":
        day = None
        rong = None
        dai = None
        
    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        UPDATE loai_go

        SET

            ten=%s,

            kieu_tinh=%s,

            day=%s,

            rong=%s,

            dai=%s

        WHERE id=%s
    """, ( ten, kieu_tinh, day, rong, dai, id))

    conn.commit()

    close_connection(conn)


def xoa_loai_go(id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        UPDATE loai_go
        SET hien_thi = FALSE
        WHERE id=%s
    """, (id,))

    conn.commit()

    close_connection(conn)

# =========================
# KHÁCH HÀNG
# =========================

def lay_ds_khach_hang():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM khach_hang
        ORDER BY ten
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data


def them_khach_hang(ten, dien_thoai, dia_chi):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO khach_hang(
            ten,
            dien_thoai,
            dia_chi
        )
        VALUES(%s,%s,%s)
    """, (ten, dien_thoai, dia_chi))

    conn.commit()

    close_connection(conn)


def sua_khach_hang(id, ten, dien_thoai, dia_chi):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE khach_hang

        SET
            ten=%s,
            dien_thoai=%s,
            dia_chi=%s

        WHERE id=%s
    """, (ten, dien_thoai, dia_chi, id))

    conn.commit()

    close_connection(conn)


def xoa_khach_hang(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM khach_hang

        WHERE id=%s
    """, (id,))

    conn.commit()

    close_connection(conn)


# =========================
# PHIẾU NHẬP
# =========================

def them_phieu_nhap(
    so_phieu,
    ngay,
    khach_hang_id,
    tong_tien,
    loai_nhap="TUOI"
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO phieu_nhap(

            so_phieu,
            ngay,
            khach_hang_id,
            tong_tien,
            loai_nhap

        )

        VALUES(%s,%s,%s,%s,%s)

        RETURNING id
    """, (
        so_phieu,
        ngay,
        khach_hang_id,
        tong_tien,
        loai_nhap
    ))

    id_phieu = cur.fetchone()["id"]

    conn.commit()
    close_connection(conn)

    return id_phieu

# =========================
# CHI TIẾT PHIẾU NHẬP
# =========================

def them_chi_tiet_phieu_nhap(
    phieu_nhap_id,
    loai_go_id,
    so_thanh,
    so_luong,
    don_gia,
    thanh_tien
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chi_tiet_phieu_nhap(

            phieu_nhap_id,
            loai_go_id,

            so_thanh,
            so_thanh_con_lai,

            so_luong,
            so_luong_con_lai,

            don_gia,
            thanh_tien

        )

        VALUES(
            %s,%s,
            %s,%s,
            %s,%s,
            %s,%s
        )
    """, (
        phieu_nhap_id,
        loai_go_id,

        so_thanh,
        so_thanh,

        so_luong,
        so_luong,

        don_gia,
        thanh_tien
    ))

    conn.commit()
    close_connection(conn)

def lay_ds_phieu_nhap(loai_nhap=None):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT

            pn.id,
            pn.so_phieu,
            pn.ngay,

            kh.ten AS khach_hang,

            pn.tong_tien,

            pn.loai_nhap

        FROM phieu_nhap pn

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        WHERE 1=1
    """

    params = []

    if loai_nhap is not None:

        sql += " AND pn.loai_nhap=%s"

        params.append(loai_nhap)

    sql += """

        ORDER BY

            pn.ngay DESC,
            pn.so_phieu DESC

    """

    cur.execute(sql, tuple(params))

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_chi_tiet_phieu_nhap(phieu_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ct.id,

            lg.id AS loai_go_id,

            lg.ten,

            lg.kieu_tinh,

            lg.day,

            lg.rong,

            lg.dai,

            ct.so_thanh,

            ct.so_luong,

            ct.don_gia,

            ct.thanh_tien

        FROM chi_tiet_phieu_nhap ct

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE ct.phieu_nhap_id=%s

        ORDER BY ct.id

    """, (phieu_id,))

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_so_phieu_moi():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(MAX(so_phieu),0)+1 AS so_phieu
        FROM phieu_nhap
    """)

    so = cur.fetchone()["so_phieu"]

    close_connection(conn)

    return so

def lay_phieu_nhap(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            pn.*,

            kh.ten AS khach_hang

        FROM phieu_nhap pn

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        WHERE pn.id=%s
    """, (id,))

    data = cur.fetchone()

    close_connection(conn)

    return data

def sua_phieu_nhap(id, ngay, khach_hang_id, tong_tien):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE phieu_nhap

        SET

            ngay=%s,

            khach_hang_id=%s,

            tong_tien=%s

        WHERE id=%s
    """, (
        ngay,
        khach_hang_id,
        tong_tien,
        id
    ))

    conn.commit()

    close_connection(conn)

def xoa_chi_tiet_phieu(phieu_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE
        FROM chi_tiet_phieu_nhap
        WHERE phieu_nhap_id=%s
    """, (phieu_id,))

    conn.commit()

    close_connection(conn)

def xoa_phieu_nhap(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE
        FROM phieu_nhap
        WHERE id=%s
    """, (id,))

    conn.commit()

    close_connection(conn)

def lay_bao_cao_nhap(
    tu_ngay,
    den_ngay,
    khach_hang_id=None,
    ten_go=None,
    loai_go_id=None,
    loai_nhap=None
):

    conn = get_connection()
    cur = conn.cursor()

    ds = []

    # =========================
    # HÀNG TƯƠI
    # =========================

    if loai_nhap in (None, "TUOI"):

        sql = """
            SELECT

                pn.ngay,
                pn.so_phieu,
                kh.ten AS khach_hang,

                '🌲 Hàng tươi' AS loai_nhap,

                lg.ten,

                '' AS phan_loai,

                lg.day,
                lg.rong,
                lg.dai,

                CASE
                    WHEN lg.kieu_tinh='TRONG_LUONG'
                    THEN ct.so_luong
                    ELSE NULL
                END AS kg,

                CASE
                    WHEN lg.kieu_tinh='M3'
                    THEN ct.so_thanh
                    ELSE NULL
                END AS thanh,

                CASE
                    WHEN lg.kieu_tinh='M3'
                    THEN ct.so_luong
                    ELSE NULL
                END AS m3,

                ct.don_gia,
                ct.thanh_tien

            FROM phieu_nhap pn

            JOIN khach_hang kh
                ON pn.khach_hang_id=kh.id

            JOIN chi_tiet_phieu_nhap ct
                ON pn.id=ct.phieu_nhap_id

            JOIN loai_go lg
                ON ct.loai_go_id=lg.id

            WHERE
                pn.loai_nhap='TUOI'
                AND pn.ngay BETWEEN %s AND %s
        """

        params = [tu_ngay, den_ngay]

        if khach_hang_id is not None:
            sql += " AND pn.khach_hang_id=%s"
            params.append(khach_hang_id)

        if ten_go is not None:
            sql += " AND lg.ten=%s"
            params.append(ten_go)

        if loai_go_id is not None:
            sql += " AND lg.id=%s"
            params.append(loai_go_id)

        sql += " ORDER BY pn.ngay,pn.so_phieu,ct.id"

        cur.execute(sql, tuple(params))

        ds.extend(cur.fetchall())

    # =========================
    # HÀNG KHÔ
    # =========================

    if loai_nhap in (None, "KHO"):

        sql = """
            SELECT

                pn.ngay,
                pn.so_phieu,
                kh.ten AS khach_hang,

                '🪵 Hàng khô' AS loai_nhap,

                lg.ten,

                pl.ten AS phan_loai,

                kp.day,
                kp.rong,
                kp.dai,

                CASE
                    WHEN lg.kieu_tinh='TRONG_LUONG'
                    THEN kp.so_luong
                    ELSE NULL
                END AS kg,

                CASE
                    WHEN lg.kieu_tinh='M3'
                    THEN kp.so_thanh
                    ELSE NULL
                END AS thanh,

                CASE
                    WHEN lg.kieu_tinh='M3'
                    THEN kp.so_luong
                    ELSE NULL
                END AS m3,

                ct.don_gia,
                ct.thanh_tien

            FROM kho_phan_loai kp

            JOIN chi_tiet_phieu_nhap ct
                ON kp.chi_tiet_phieu_nhap_id=ct.id

            JOIN phieu_nhap pn
                ON ct.phieu_nhap_id=pn.id

            JOIN khach_hang kh
                ON pn.khach_hang_id=kh.id

            JOIN loai_go lg
                ON ct.loai_go_id=lg.id

            JOIN phan_loai_go pl
                ON kp.phan_loai_go_id=pl.id

            WHERE
                pn.loai_nhap='KHO'
                AND pn.ngay BETWEEN %s AND %s
        """

        params = [tu_ngay, den_ngay]

        if khach_hang_id is not None:
            sql += " AND pn.khach_hang_id=%s"
            params.append(khach_hang_id)

        if ten_go is not None:
            sql += " AND lg.ten=%s"
            params.append(ten_go)

        if loai_go_id is not None:
            sql += " AND lg.id=%s"
            params.append(loai_go_id)

        sql += " ORDER BY pn.ngay,pn.so_phieu,kp.id"

        cur.execute(sql, tuple(params))

        ds.extend(cur.fetchall())

    ds.sort(
        key=lambda x: (
            x["ngay"],
            x["so_phieu"]
        )
    )

    close_connection(conn)

    return ds

def lay_kho_tuoi(
    khach_hang_id=None,
    ten_go=None,
    loai_go_id=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            ct.id,
            pn.ngay,
            pn.so_phieu,
            kh.ten AS khach_hang,

            lg.ten,

            lg.day,
            lg.rong,
            lg.dai,

            CASE
                WHEN lg.kieu_tinh = 'TRONG_LUONG'
                THEN ct.so_luong_con_lai
                ELSE NULL
            END AS kg,

            CASE
                WHEN lg.kieu_tinh = 'M3'
                THEN ct.so_thanh_con_lai
                ELSE NULL
            END AS thanh,

            CASE
                WHEN lg.kieu_tinh = 'M3'
                THEN ct.so_luong_con_lai
                ELSE NULL
            END AS m3

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            ct.trang_thai = 'TUOI'
            AND
            (
                (
                    lg.kieu_tinh = 'TRONG_LUONG'
                    AND ct.so_luong_con_lai > 0
                )
                OR
                (
                    lg.kieu_tinh = 'M3'
                    AND ct.so_thanh_con_lai > 0
                )
            )
    """

    params = []

    if khach_hang_id is not None:
        sql += " AND pn.khach_hang_id = %s"
        params.append(khach_hang_id)

    # Lọc theo tên gỗ
    if ten_go is not None:
        sql += " AND lg.ten = %s"
        params.append(ten_go)

    # Nếu đã chọn quy cách thì lọc tiếp theo id
    if loai_go_id is not None:
        sql += " AND lg.id = %s"
        params.append(loai_go_id)

    sql += """
        ORDER BY
            pn.ngay,
            pn.so_phieu,
            ct.id
    """

    cur.execute(sql, tuple(params))

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_ham_say():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            so_ham,
            COUNT(*) AS so_lo
        FROM ham_say
        WHERE trang_thai='DANG_SAY'
        GROUP BY so_ham
        ORDER BY so_ham
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def them_ham_say(
    chi_tiet_phieu_nhap_id,
    so_ham,
    so_luong,
    so_thanh
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ham_say(

            chi_tiet_phieu_nhap_id,
            so_ham,
            so_luong,
            so_thanh

        )

        VALUES(%s,%s,%s,%s)
    """, (
        chi_tiet_phieu_nhap_id,
        so_ham,
        so_luong,
        so_thanh
    ))

    conn.commit()
    close_connection(conn)

def lay_chi_tiet_ham(so_ham):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            hs.id,

            pn.ngay,
            pn.so_phieu,
            kh.ten AS khach_hang,
                
            lg.ten,

            lg.day,
            lg.rong,
            lg.dai,

            CASE
                WHEN lg.kieu_tinh='TRONG_LUONG'
                THEN hs.so_luong
                ELSE NULL
            END AS kg,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_thanh
                ELSE NULL
            END AS thanh,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_luong
                ELSE NULL
            END AS m3,

            hs.ngay_vao

        FROM ham_say hs

        JOIN chi_tiet_phieu_nhap ct
            ON hs.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            hs.so_ham = %s
            AND hs.trang_thai = 'DANG_SAY'

        ORDER BY
            hs.ngay_vao

    """, (so_ham,))

    data = cur.fetchall()

    close_connection(conn)

    return data

def dem_lo_trong_ham():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            so_ham,
            COUNT(*)

        FROM ham_say

        WHERE trang_thai='DANG_SAY'

        GROUP BY so_ham
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_kho_tuoi_kg():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ct.id,
            pn.ngay,
            pn.so_phieu,
            kh.ten AS khach_hang,

            lg.ten,

            ct.so_luong AS kg

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            lg.kieu_tinh = 'TRONG_LUONG'
            AND ct.trang_thai = 'TUOI'

        ORDER BY
            pn.ngay,
            pn.so_phieu
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data
def dua_kg_vao_ham(
    chi_tiet_id,
    so_ham
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT so_luong_con_lai
        FROM chi_tiet_phieu_nhap
        WHERE id=%s
    """, (chi_tiet_id,))

    row = cur.fetchone()

    kg = row["so_luong_con_lai"]

    cur.execute("""
        INSERT INTO ham_say(
            chi_tiet_phieu_nhap_id,
            so_ham,
            so_luong
        )
        VALUES(%s,%s,%s)
        RETURNING id
    """, (
        chi_tiet_id,
        so_ham,
        kg
    ))

    ham_say_id = cur.fetchone()["id"]
    ghi_lich_su_ham(
        cur,
        ham_say_id,
        chi_tiet_id,
        so_ham,
        "VAO_HAM",
        kg,
        None,
        "KG"
    )

    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET
            trang_thai='SAY',
            so_luong_con_lai=0
        WHERE id=%s
    """, (chi_tiet_id,))

    conn.commit()
    close_connection(conn)

def lay_kho_tuoi_m3():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ct.id,

            pn.ngay,
            pn.so_phieu,

            kh.ten AS khach_hang,

            lg.ten,

            lg.day,
            lg.rong,
            lg.dai,

            ct.so_thanh_con_lai AS thanh,
            ct.so_luong_con_lai AS m3

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            lg.kieu_tinh='M3'
            AND ct.trang_thai='TUOI'
            AND ct.so_thanh_con_lai > 0

        ORDER BY
            pn.ngay,
            pn.so_phieu
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def dua_m3_vao_ham(
    chi_tiet_id,
    so_ham,
    so_thanh
):

    conn = get_connection()
    cur = conn.cursor()

    # Lấy số còn lại của lô gỗ
    cur.execute("""
        SELECT
            so_thanh_con_lai,
            so_luong_con_lai
        FROM chi_tiet_phieu_nhap
        WHERE id=%s
    """, (chi_tiet_id,))

    row = cur.fetchone()

    tong_thanh = row["so_thanh_con_lai"]
    tong_m3 = row["so_luong_con_lai"]

    # Kiểm tra nhập quá
    if so_thanh > tong_thanh:

        close_connection(conn)

        raise ValueError("Số thanh vượt quá số còn lại.")

    # Tính m3 tương ứng
    m3 = tong_m3 * so_thanh / tong_thanh

    # Ghi vào hầm
    cur.execute("""
        INSERT INTO ham_say(
            chi_tiet_phieu_nhap_id,
            so_ham,
            so_thanh,
            so_luong
        )
        VALUES(%s,%s,%s,%s)
        RETURNING id
    """, (
        chi_tiet_id,
        so_ham,
        so_thanh,
        m3
    ))
    ham_say_id = cur.fetchone()["id"]
    ghi_lich_su_ham(
        cur,
        ham_say_id,
        chi_tiet_id,
        so_ham,
        "VAO_HAM",
        m3,
        so_thanh,
        "M3"
    )

    # Cập nhật số còn lại
    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET
            so_thanh_con_lai = so_thanh_con_lai - %s,
            so_luong_con_lai = so_luong_con_lai - %s
        WHERE id=%s
    """, (
        so_thanh,
        m3,
        chi_tiet_id
    ))

    # Nếu hết thì chuyển trạng thái
    cur.execute("""
        SELECT
            so_thanh_con_lai
        FROM chi_tiet_phieu_nhap
        WHERE id=%s
    """, (chi_tiet_id,))

    con_lai = cur.fetchone()["so_thanh_con_lai"]

    if con_lai <= 0:

        cur.execute("""
            UPDATE chi_tiet_phieu_nhap
            SET trang_thai='SAY'
            WHERE id=%s
        """, (chi_tiet_id,))

    conn.commit()

    close_connection(conn)

def ra_ham(
    ham_say_id,
    kg_ra=None,
    thanh_ra=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            chi_tiet_phieu_nhap_id,
            so_ham,
            so_luong,
            so_thanh
        FROM ham_say
        WHERE id=%s
    """, (ham_say_id,))

    row = cur.fetchone()
    # Đánh dấu lô này đã từng ra hầm
    cur.execute("""
        UPDATE ham_say
        SET da_ra_ham = TRUE
        WHERE id=%s
    """, (ham_say_id,))

    # ==========================
    # GỖ KG
    # ==========================
    if row["so_thanh"] is None:

        tong_kg = row["so_luong"]
        kg_ra = Decimal(str(kg_ra))

       
        # Kiểm tra nhập quá
        if kg_ra > tong_kg:
            close_connection(conn)
            raise ValueError(f"Chỉ còn {tong_kg} kg trong hầm.")

        # Ra hết
        if kg_ra == tong_kg:

            cur.execute("""
                UPDATE ham_say
                SET
                    trang_thai='DA_SAY',
                    ngay_ra=NOW()
                WHERE id=%s
            """, (ham_say_id,))

            ham_say_moi = ham_say_id

        else:

            kg_con = tong_kg - kg_ra

            # Cập nhật số còn trong hầm
            cur.execute("""
                UPDATE ham_say
                SET so_luong=%s
                WHERE id=%s
            """, (
                kg_con,
                ham_say_id
            ))

            # Tạo lô đã ra
            cur.execute("""
                INSERT INTO ham_say(
                    chi_tiet_phieu_nhap_id,
                    so_ham,
                    so_luong,
                    trang_thai,
                    ngay_vao,
                    ngay_ra
                )
                VALUES(
                    %s,%s,%s,
                    'DA_SAY',
                    NOW(),
                    NOW()
                )
                RETURNING id
            """, (
                row["chi_tiet_phieu_nhap_id"],
                row["so_ham"],
                kg_ra
            ))

            ham_say_moi = cur.fetchone()["id"]

    # ==========================
    # GỖ M3
    # ==========================
    else:

        tong_thanh = row["so_thanh"]
        tong_m3 = row["so_luong"]

        # Kiểm tra nhập quá
        if thanh_ra > tong_thanh:
            close_connection(conn)
            raise ValueError(f"Chỉ còn {tong_thanh} thanh trong hầm.")

        # Ra hết
        if thanh_ra == tong_thanh:

            cur.execute("""
                UPDATE ham_say
                SET
                    trang_thai='DA_SAY',
                    ngay_ra=NOW()
                WHERE id=%s
            """, (ham_say_id,))

            ham_say_moi = ham_say_id

        else:

            m3_ra = tong_m3 * thanh_ra / tong_thanh

            m3_con = tong_m3 - m3_ra

            thanh_con = tong_thanh - thanh_ra

            # Còn trong hầm
            cur.execute("""
                UPDATE ham_say
                SET
                    so_thanh=%s,
                    so_luong=%s
                WHERE id=%s
            """, (
                thanh_con,
                m3_con,
                ham_say_id
            ))

            # Lô đã ra
            cur.execute("""
                INSERT INTO ham_say(
                    chi_tiet_phieu_nhap_id,
                    so_ham,
                    so_thanh,
                    so_luong,
                    trang_thai,
                    ngay_vao,
                    ngay_ra
                )
                VALUES(
                    %s,%s,%s,%s,
                    'DA_SAY',
                    NOW(),
                    NOW()
                )
                RETURNING id
            """, (
                row["chi_tiet_phieu_nhap_id"],
                row["so_ham"],
                thanh_ra,
                m3_ra
            ))

            ham_say_moi = cur.fetchone()["id"]

    # ==========================
    # Đưa vào kho khô
    # ==========================
    cur.execute("""
        INSERT INTO kho_kho(
            ham_say_id
        )
        VALUES(%s)
    """, (ham_say_moi,))

    # ==========================
    # Ghi lịch sử
    # ==========================

    if row["so_thanh"] is None:

        ghi_lich_su_ham(
            cur,
            ham_say_moi,
            row["chi_tiet_phieu_nhap_id"],
            row["so_ham"],
            "RA_HAM",
            kg_ra,
            None,
            "KG"
        )

    else:

        if thanh_ra == tong_thanh:
            m3_ra = tong_m3

        ghi_lich_su_ham(
            cur,
            ham_say_moi,
            row["chi_tiet_phieu_nhap_id"],
            row["so_ham"],
            "RA_HAM",
            m3_ra,
            thanh_ra,
            "M3"
        )

    conn.commit()

    close_connection(conn)

def lay_kho_kho(
    khach_hang_id=None,
    loai_go_id=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT

            kk.id,

            pn.ngay,
            pn.so_phieu,

            kh.ten AS khach_hang,

            lg.ten,
            lg.kieu_tinh,

            lg.day,
            lg.rong,
            lg.dai,

            CASE
                WHEN lg.kieu_tinh='TRONG_LUONG'
                THEN hs.so_luong
                ELSE NULL
            END AS kg,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_thanh
                ELSE NULL
            END AS thanh,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_luong
                ELSE NULL
            END AS m3,

            hs.ngay_vao,
            hs.ngay_ra

        FROM kho_kho kk

        JOIN ham_say hs
            ON kk.ham_say_id = hs.id

        JOIN chi_tiet_phieu_nhap ct
            ON hs.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE 1=1
          AND (
              (lg.kieu_tinh = 'TRONG_LUONG' AND hs.so_luong > 0)
              OR 
              (lg.kieu_tinh = 'M3' AND hs.so_thanh > 0)
          )
    """

    params = []

    if khach_hang_id is not None:
        sql += " AND kh.id=%s"
        params.append(khach_hang_id)

    if loai_go_id is not None:
        sql += " AND lg.id=%s"
        params.append(loai_go_id)

    sql += """
        ORDER BY
            hs.ngay_ra,
            pn.so_phieu
    """

    cur.execute(sql, tuple(params))

    data = cur.fetchall()

    close_connection(conn)

    return data

# =========================
# PHÂN LOẠI GỖ
# =========================

def lay_ds_phan_loai_go():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM phan_loai_go
        WHERE hien_thi=TRUE
        ORDER BY ten
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data


def them_phan_loai_go(
    ten
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO phan_loai_go(
            ten
        )
        VALUES(%s)
    """, (
        ten,
    ))

    conn.commit()

    close_connection(conn)


def sua_phan_loai_go(
    id,
    ten
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE phan_loai_go

        SET
            ten=%s

        WHERE id=%s
    """, (
        ten,
        id
    ))

    conn.commit()

    close_connection(conn)


def xoa_phan_loai_go(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE phan_loai_go
        SET hien_thi=FALSE
        WHERE id=%s
    """, (id,))

    conn.commit()

    close_connection(conn)

def lay_ds_phan_loai():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            ten
        FROM phan_loai_go
        WHERE hien_thi=TRUE
        ORDER BY ten
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def luu_phan_loai(
    kho_kho_id,
    ds_phan_loai
):

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Lấy hầm sấy và chi tiết phiếu nhập
        cur.execute("""
            SELECT
                hs.id AS ham_say_id,
                hs.chi_tiet_phieu_nhap_id
            FROM kho_kho kk
            JOIN ham_say hs
                ON kk.ham_say_id = hs.id
            WHERE kk.id=%s
        """, (kho_kho_id,))

        row = cur.fetchone()


        if row is None:
            raise Exception("Không tìm thấy kho.")

        ham_say_id = row["ham_say_id"]
        chi_tiet_phieu_nhap_id = row["chi_tiet_phieu_nhap_id"]

        tong_so_luong = 0
        tong_so_thanh = 0

        for item in ds_phan_loai:


            cur.execute("""
                SELECT id
                FROM phan_loai_go
                WHERE ten=%s
            """, (item["loai"],))

            pl = cur.fetchone()


            if pl is None:
                raise Exception(
                    f"Không tìm thấy phân loại: {item['loai']}"
                )

            so_luong = float(item.get("kg", 0) or item.get("m3", 0))
            so_thanh = int(item.get("thanh", 0))


            cur.execute("""
                INSERT INTO kho_phan_loai(
                    kho_kho_id,
                    chi_tiet_phieu_nhap_id,
                    phan_loai_go_id,
                    day,
                    rong,
                    dai,
                    so_luong,
                    so_thanh,
                    ngay
                )
                VALUES(
                    %s,%s,%s,
                    %s,%s,%s,
                    %s,%s,
                    NOW()
                )
            """, (
                kho_kho_id,
                chi_tiet_phieu_nhap_id,
                pl["id"],
                item["day"],
                item["rong"],
                item["dai"],
                so_luong,
                so_thanh
            ))

           

            tong_so_luong += so_luong
            tong_so_thanh += so_thanh

        cur.execute("""
            SELECT lg.kieu_tinh
            FROM ham_say hs
            JOIN chi_tiet_phieu_nhap ct
                ON hs.chi_tiet_phieu_nhap_id = ct.id
            JOIN loai_go lg
                ON ct.loai_go_id = lg.id
            WHERE hs.id=%s
        """, (ham_say_id,))

        kieu = cur.fetchone()["kieu_tinh"]

       

        if kieu == "TRONG_LUONG":

            cur.execute("""
                UPDATE ham_say
                SET so_luong = so_luong - %s
                WHERE id=%s
            """, (
                tong_so_luong,
                ham_say_id
            ))

            cur.execute("""
                SELECT so_luong
                FROM ham_say
                WHERE id=%s
            """, (ham_say_id,))

            con_lai = cur.fetchone()["so_luong"]

        else:

            cur.execute("""
                UPDATE ham_say
                SET
                    so_thanh = so_thanh - %s,
                    so_luong = so_luong - %s
                WHERE id=%s
            """, (
                tong_so_thanh,
                tong_so_luong,
                ham_say_id
            ))

            cur.execute("""
                SELECT so_thanh
                FROM ham_say
                WHERE id=%s
            """, (ham_say_id,))

            con_lai = cur.fetchone()["so_thanh"]

       

        if con_lai <= 0:

            # Không xóa bản ghi kho_kho để giữ liên kết
            pass

        conn.commit()

        

    except Exception as e:

        conn.rollback()

        raise

    finally:

        close_connection(conn)

def lay_kho_da_phan_loai(
    khach_hang_id=None,
    ten_go=None,
    ds_quy_cach=None,
    phan_loai_go_id=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT

            kp.id AS kho_phan_loai_id,

            pn.ngay,

            pn.so_phieu,

            kh.ten AS khach_hang,

            lg.ten,
            lg.kieu_tinh,

            kp.day,
            kp.rong,
            kp.dai,

            pl.id AS phan_loai_go_id,
            pl.ten AS phan_loai,

            CASE
                WHEN lg.kieu_tinh='TRONG_LUONG'
                THEN kp.so_luong
                ELSE NULL
            END AS kg,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN kp.so_thanh
                ELSE NULL
            END AS thanh,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN kp.so_luong
                ELSE NULL
            END AS m3

        FROM kho_phan_loai kp

        JOIN chi_tiet_phieu_nhap ct
            ON kp.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        JOIN phan_loai_go pl
            ON kp.phan_loai_go_id = pl.id

        WHERE 1=1
    """

    params = []

    if khach_hang_id is not None:

        sql += " AND kh.id=%s"
        params.append(khach_hang_id)

    if ten_go is not None:

        sql += " AND lg.ten=%s"
        params.append(ten_go)
    
    if phan_loai_go_id is not None:

        sql += " AND pl.id=%s"
        params.append(phan_loai_go_id)

    if ds_quy_cach:

        sql += " AND ("

        dieu_kien = []

        for qc in ds_quy_cach:

            dieu_kien.append(
                "(kp.day=%s AND kp.rong=%s AND kp.dai=%s)"
            )

            params.extend([
                qc["day"],
                qc["rong"],
                qc["dai"]
            ])

        sql += " OR ".join(dieu_kien)

        sql += ")"

    sql += """
        ORDER BY
            pn.ngay,
            pn.so_phieu,
            kp.id
    """

    cur.execute(sql, tuple(params))

    data = cur.fetchall()

    close_connection(conn)

    return data
def lay_ds_thu_hoi_ham():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            hs.id,

            hs.so_ham,

            pn.so_phieu,

            kh.ten AS khach_hang,

            lg.ten,
                
            lg.day,
            lg.rong,
            lg.dai,

            CASE
                WHEN lg.kieu_tinh='TRONG_LUONG'
                THEN hs.so_luong
                ELSE NULL
            END AS kg,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_thanh
                ELSE NULL
            END AS thanh,

            CASE
                WHEN lg.kieu_tinh='M3'
                THEN hs.so_luong
                ELSE NULL
            END AS m3,

            hs.ngay_vao

        FROM ham_say hs

        JOIN chi_tiet_phieu_nhap ct
            ON hs.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            hs.trang_thai = 'DANG_SAY'
            AND hs.da_ra_ham = FALSE

        ORDER BY
            hs.so_ham,
            hs.ngay_vao

    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def thu_hoi_ham(ham_say_id):

    conn = get_connection()
    cur = conn.cursor()

    try:

        # Lấy thông tin lô trong hầm
        cur.execute("""
            SELECT
                chi_tiet_phieu_nhap_id,
                so_ham,
                so_luong,
                so_thanh,
                da_ra_ham
            FROM ham_say
            WHERE id=%s
        """, (ham_say_id,))

        hs = cur.fetchone()

        if hs is None:
            raise Exception("Không tìm thấy lô trong hầm.")

        # Không cho thu hồi nếu đã từng ra hầm
        if hs["da_ra_ham"]:
            raise Exception("Lô này đã phát sinh ra hầm, không thể thu hồi.")

        # ==========================
        # Gỗ KG
        # ==========================
        if hs["so_thanh"] is None:

            cur.execute("""
                UPDATE chi_tiet_phieu_nhap
                SET
                    so_luong_con_lai = so_luong_con_lai + %s,
                    trang_thai = 'TUOI'
                WHERE id=%s
            """, (
                hs["so_luong"],
                hs["chi_tiet_phieu_nhap_id"]
            ))

            ghi_lich_su_ham(
                cur,
                ham_say_id,
                hs["chi_tiet_phieu_nhap_id"],
                hs["so_ham"],
                "THU_HOI",
                hs["so_luong"],
                None,
                "KG"
            )

        # ==========================
        # Gỗ M3
        # ==========================
        else:

            cur.execute("""
                UPDATE chi_tiet_phieu_nhap
                SET
                    so_thanh_con_lai = so_thanh_con_lai + %s,
                    so_luong_con_lai = so_luong_con_lai + %s,
                    trang_thai = 'TUOI'
                WHERE id=%s
            """, (
                hs["so_thanh"],
                hs["so_luong"],
                hs["chi_tiet_phieu_nhap_id"]
            ))

            ghi_lich_su_ham(
                cur,
                ham_say_id,
                hs["chi_tiet_phieu_nhap_id"],
                hs["so_ham"],
                "THU_HOI",
                hs["so_luong"],
                hs["so_thanh"],
                "M3"
            )

        # Xóa khỏi hầm
        cur.execute("""
            DELETE FROM ham_say
            WHERE id=%s
        """, (ham_say_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        close_connection(conn)

def ghi_lich_su_ham(
    cur,
    ham_say_id,
    chi_tiet_id,
    so_ham,
    hanh_dong,
    so_luong,
    so_thanh,
    loai_hang
):

    cur.execute("""
        INSERT INTO lich_su_ham(

            ham_say_id,
            chi_tiet_phieu_nhap_id,
            so_ham,
            hanh_dong,
            so_luong,
            so_thanh,
            loai_hang

        )
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """, (
        ham_say_id,
        chi_tiet_id,
        so_ham,
        hanh_dong,
        so_luong,
        so_thanh,
        loai_hang
    ))

def lay_lich_su_ham(
    tu_ngay,
    den_ngay,
    khach_hang_id=None,
    ten_go=None,
    loai_go_id=None,
    hanh_dong=None,
    so_ham=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT

            ls.ngay,

            ls.so_ham,

            pn.so_phieu,

            kh.ten,

            lg.ten AS ten_go,

            ls.hanh_dong,

            ls.so_luong,

            ls.so_thanh,

            ls.loai_hang

        FROM lich_su_ham ls

        JOIN chi_tiet_phieu_nhap ct
            ON ls.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE
            ls.ngay >= %s
            AND ls.ngay < (%s::date + INTERVAL '1 day')
            AND ls.hanh_dong <> 'THU_HOI'
    """

    params = [tu_ngay, den_ngay]

    if khach_hang_id is not None:
        sql += " AND kh.id = %s"
        params.append(khach_hang_id)

    # Lọc theo tên gỗ
    if ten_go is not None:
        sql += " AND lg.ten = %s"
        params.append(ten_go)

    # Lọc theo quy cách
    if loai_go_id is not None:
        sql += " AND lg.id = %s"
        params.append(loai_go_id)

    # Lọc theo thao tác
    if hanh_dong in ("VAO_HAM", "RA_HAM"):
        sql += " AND ls.hanh_dong = %s"
        params.append(hanh_dong)
    if so_ham is not None:

        sql += " AND ls.so_ham = %s"

        params.append(so_ham)

    sql += """
        ORDER BY
            ls.ngay DESC,
            ls.id DESC
    """

    cur.execute(sql, tuple(params))

    data = cur.fetchall()

    close_connection(conn)

    return data

def them_cong_no(
    khach_hang_id,
    ngay,
    loai,
    so_tien,
    phieu_nhap_id=None,
    ghi_chu=""
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cong_no(
            khach_hang_id,
            ngay,
            loai,
            so_tien,
            phieu_nhap_id,
            ghi_chu
        )
        VALUES(%s,%s,%s,%s,%s,%s)
    """, (
        khach_hang_id,
        ngay,
        loai,
        so_tien,
        phieu_nhap_id,
        ghi_chu
    ))

    conn.commit()

    close_connection(conn)

def sua_cong_no(
    phieu_nhap_id,
    khach_hang_id,
    ngay,
    loai,
    so_tien,
    ghi_chu=""
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE cong_no
        SET
            khach_hang_id=%s,
            ngay=%s,
            so_tien=%s,
            ghi_chu=%s
        WHERE
            phieu_nhap_id=%s
            AND loai=%s
    """, (
        khach_hang_id,
        ngay,
        so_tien,
        ghi_chu,
        phieu_nhap_id,
        loai
    ))

    conn.commit()
    close_connection(conn)

def xoa_cong_no(phieu_nhap_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE
        FROM cong_no
        WHERE phieu_nhap_id=%s
    """, (phieu_nhap_id,))

    conn.commit()
    close_connection(conn)

def lay_no_phai_thu():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            cn.id,

            pn.so_phieu,

            cn.ngay,

            kh.ten AS khach_hang,

            cn.so_tien,

            COALESCE(
                SUM(tt.so_tien),
                0
            ) AS da_thanh_toan,

            cn.so_tien
            - COALESCE(
                SUM(tt.so_tien),
                0
            ) AS con_lai

        FROM cong_no cn

        JOIN khach_hang kh
            ON cn.khach_hang_id = kh.id

        LEFT JOIN phieu_nhap pn
            ON cn.phieu_nhap_id = pn.id

        LEFT JOIN thanh_toan tt
            ON cn.id = tt.cong_no_id

        WHERE cn.loai = 'CONG_SAY'

        GROUP BY

            cn.id,
            pn.so_phieu,
            cn.ngay,
            kh.ten,
            cn.so_tien

        ORDER BY

            cn.ngay,
            pn.so_phieu

    """)

    data = cur.fetchall()

    close_connection(conn)

    return data


def lay_ds_ten_go():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ten
        FROM loai_go
        WHERE hien_thi = TRUE
        ORDER BY ten
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_ds_quy_cach(ten_go):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            day,
            rong,
            dai
        FROM loai_go
        WHERE
            hien_thi = TRUE
            AND ten=%s
            AND kieu_tinh='M3'
        ORDER BY
            day,
            rong,
            dai
    """, (ten_go,))

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_ds_quy_cach_da_phan_loai(ten_go):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT

            kp.day,
            kp.rong,
            kp.dai

        FROM kho_phan_loai kp

        JOIN chi_tiet_phieu_nhap ct
            ON kp.chi_tiet_phieu_nhap_id = ct.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE lg.ten = %s

        ORDER BY
            kp.day,
            kp.rong,
            kp.dai
    """, (ten_go,))

    data = cur.fetchall()

    close_connection(conn)

    return data

def them_chi_tiet_nhap_hang_kho(
    phieu_nhap_id, loai_go_id, phan_loai_go_id,
    day, rong, dai, so_thanh, so_luong, don_gia, thanh_tien
):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Thêm vào chi tiết phiếu nhập (trạng thái đi thẳng vào kho phân loại)
        cur.execute("""
            INSERT INTO chi_tiet_phieu_nhap(
                phieu_nhap_id, loai_go_id, so_thanh, so_thanh_con_lai,
                so_luong, so_luong_con_lai, don_gia, thanh_tien, trang_thai
            )
            VALUES (%s, %s, %s, 0, %s, 0, %s, %s, 'KHO_PHAN_LOAI')
            RETURNING id
        """, (phieu_nhap_id, loai_go_id, so_thanh, so_luong, don_gia, thanh_tien))
        
        chi_tiet_id = cur.fetchone()["id"]
        
        # 2. Đưa thẳng dữ liệu vào kho đã phân loại (kho_kho_id nhận NULL vì không qua hầm sấy)
        cur.execute("""
            INSERT INTO kho_phan_loai(
                kho_kho_id, chi_tiet_phieu_nhap_id, phan_loai_go_id,
                day, rong, dai, so_thanh, so_luong, ngay
            )
            VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (chi_tiet_id, phan_loai_go_id, day, rong, dai, so_thanh, so_luong))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_connection(conn)

def lay_chi_tiet_nhap_hang_kho(phieu_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            ct.id,
            lg.id AS loai_go_id,
            lg.ten,
            lg.kieu_tinh,
            kpl.phan_loai_go_id,
            plg.ten AS ten_phan_loai,
            kpl.day,
            kpl.rong,
            kpl.dai,
            ct.so_thanh,
            ct.so_luong,
            ct.don_gia,
            ct.thanh_tien
        FROM chi_tiet_phieu_nhap ct
        JOIN loai_go lg ON ct.loai_go_id = lg.id
        LEFT JOIN kho_phan_loai kpl ON ct.id = kpl.chi_tiet_phieu_nhap_id
        LEFT JOIN phan_loai_go plg ON kpl.phan_loai_go_id = plg.id
        WHERE ct.phieu_nhap_id = %s
        ORDER BY ct.id
    """, (phieu_id,))
    ds = cur.fetchall()
    close_connection(conn)
    return ds

def cap_nhat_nhap_hang_kho(
    chi_tiet_id, loai_go_id, phan_loai_go_id,
    day, rong, dai, so_thanh, so_luong, don_gia, thanh_tien
):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Cập nhật bảng chi tiết phiếu nhập
        cur.execute("""
            UPDATE chi_tiet_phieu_nhap
            SET
                loai_go_id=%s,
                so_thanh=%s,
                so_luong=%s,
                don_gia=%s,
                thanh_tien=%s
            WHERE id=%s
        """, (loai_go_id, so_thanh, so_luong, don_gia, thanh_tien, chi_tiet_id))

        # 2. Cập nhật bảng kho đã phân loại tương ứng
        cur.execute("""
            UPDATE kho_phan_loai
            SET
                phan_loai_go_id=%s,
                day=%s,
                rong=%s,
                dai=%s,
                so_thanh=%s,
                so_luong=%s
            WHERE chi_tiet_phieu_nhap_id=%s
        """, (phan_loai_go_id, day, rong, dai, so_thanh, so_luong, chi_tiet_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_connection(conn)

def lay_ds_ham():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            so_ham
        FROM lich_su_ham
        ORDER BY so_ham
    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def them_thanh_toan(
    cong_no_id,
    ngay,
    so_tien,
    ghi_chu=""
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO thanh_toan(
            cong_no_id,
            ngay,
            so_tien,
            ghi_chu
        )
        VALUES(%s,%s,%s,%s)
    """,(
        cong_no_id,
        ngay,
        so_tien,
        ghi_chu
    ))

    conn.commit()
    close_connection(conn)

def lay_ds_thanh_toan(cong_no_id):

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT
            id,
            ngay,
            so_tien,
            ghi_chu
        FROM thanh_toan
        WHERE cong_no_id=%s
        ORDER BY ngay,id
    """,(cong_no_id,))

    ds=cur.fetchall()

    close_connection(conn)

    return ds

def lay_no_phai_tra():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            cn.id,

            pn.so_phieu,

            cn.ngay,

            kh.ten AS khach_hang,

            cn.so_tien,

            COALESCE(
                SUM(tt.so_tien),
                0
            ) AS da_thanh_toan,

            cn.so_tien
            - COALESCE(
                SUM(tt.so_tien),
                0
            ) AS con_lai

        FROM cong_no cn

        JOIN khach_hang kh
            ON cn.khach_hang_id = kh.id

        LEFT JOIN phieu_nhap pn
            ON cn.phieu_nhap_id = pn.id

        LEFT JOIN thanh_toan tt
            ON cn.id = tt.cong_no_id

        WHERE cn.loai = 'MUA_GO'

        GROUP BY

            cn.id,
            pn.so_phieu,
            cn.ngay,
            kh.ten,
            cn.so_tien

        ORDER BY

            cn.ngay,
            pn.so_phieu

    """)

    data = cur.fetchall()

    close_connection(conn)

    return data
def lay_tong_hop_cong_no():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            kh.id,

            kh.ten,

            COALESCE(
                SUM(
                    CASE
                        WHEN cn.loai='CONG_SAY'
                        THEN cn.so_tien - COALESCE(tt.da_thanh_toan,0)
                        ELSE 0
                    END
                ),0
            ) AS no_phai_thu,

            COALESCE(
                SUM(
                    CASE
                        WHEN cn.loai='MUA_GO'
                        THEN cn.so_tien - COALESCE(tt.da_thanh_toan,0)
                        ELSE 0
                    END
                ),0
            ) AS no_phai_tra,

            COALESCE(
                SUM(
                    CASE
                        WHEN cn.loai='CONG_SAY'
                        THEN cn.so_tien - COALESCE(tt.da_thanh_toan,0)
                        ELSE 0
                    END
                ),0
            )
            -
            COALESCE(
                SUM(
                    CASE
                        WHEN cn.loai='MUA_GO'
                        THEN cn.so_tien - COALESCE(tt.da_thanh_toan,0)
                        ELSE 0
                    END
                ),0
            ) AS chenh_lech

        FROM khach_hang kh

        LEFT JOIN cong_no cn
            ON kh.id = cn.khach_hang_id

        LEFT JOIN (
            SELECT
                cong_no_id,
                SUM(so_tien) AS da_thanh_toan
            FROM thanh_toan
            GROUP BY cong_no_id
        ) tt
            ON cn.id = tt.cong_no_id

        GROUP BY
            kh.id,
            kh.ten

        ORDER BY
            kh.ten
    """)

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_chi_tiet_cong_no(cong_no_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            cn.id,

            cn.loai,

            cn.ngay,

            cn.so_tien,

            pn.so_phieu,

            kh.ten AS khach_hang,

            COALESCE(SUM(tt.so_tien),0) AS da_thanh_toan,

            cn.so_tien - COALESCE(SUM(tt.so_tien),0) AS con_lai

        FROM cong_no cn

        JOIN khach_hang kh
            ON cn.khach_hang_id = kh.id

        LEFT JOIN phieu_nhap pn
            ON cn.phieu_nhap_id = pn.id

        LEFT JOIN thanh_toan tt
            ON cn.id = tt.cong_no_id

        WHERE cn.id=%s

        GROUP BY
            cn.id,
            cn.loai,
            cn.ngay,
            cn.so_tien,
            pn.so_phieu,
            kh.ten
    """, (cong_no_id,))

    data = cur.fetchone()

    close_connection(conn)

    return data

def lay_chi_tiet_phieu_cong_no(cong_no_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            pn.so_phieu,

            pn.ngay,

            kh.ten AS khach_hang,

            lg.ten,

            lg.kieu_tinh,

            lg.day,

            lg.rong,

            lg.dai,

            ct.so_thanh,

            ct.so_luong,

            ct.don_gia,

            ct.thanh_tien

        FROM cong_no cn

        JOIN phieu_nhap pn
            ON cn.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN chi_tiet_phieu_nhap ct
            ON pn.id = ct.phieu_nhap_id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE cn.id = %s

        ORDER BY ct.id

    """, (cong_no_id,))

    data = cur.fetchall()

    close_connection(conn)

    return data

def lay_chi_tiet_tong_hop(khach_hang_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            cn.id,

            cn.loai,

            pn.so_phieu,

            cn.ngay,

            cn.so_tien,

            COALESCE(SUM(tt.so_tien),0) AS da_thanh_toan,

            cn.so_tien
            - COALESCE(SUM(tt.so_tien),0) AS con_lai

        FROM cong_no cn

        LEFT JOIN phieu_nhap pn
            ON cn.phieu_nhap_id = pn.id

        LEFT JOIN thanh_toan tt
            ON cn.id = tt.cong_no_id

        WHERE cn.khach_hang_id=%s

        GROUP BY

            cn.id,
            cn.loai,
            pn.so_phieu,
            cn.ngay,
            cn.so_tien

        ORDER BY

            cn.loai,
            cn.ngay,
            pn.so_phieu

    """, (khach_hang_id,))

    data = cur.fetchall()

    close_connection(conn)

    return data