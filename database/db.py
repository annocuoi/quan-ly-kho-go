import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config import DATABASE
from datetime import date

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
# =========================
# TẠO DATABASE
# =========================

def tao_database():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_info(
            id INTEGER PRIMARY KEY,
            version INTEGER
        )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM app_info")

    if cur.fetchone()["count"] > 0:
        close_connection(conn)
        return

    # =========================
    # LOẠI GỖ
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS loai_go(

        id SERIAL PRIMARY KEY,

        ma_go VARCHAR(50) UNIQUE NOT NULL,

        ten_go VARCHAR(255) NOT NULL,

        kieu_tinh VARCHAR(20) NOT NULL DEFAULT 'M3',

        day DOUBLE PRECISION,

        rong DOUBLE PRECISION,

        dai DOUBLE PRECISION,

        trang_thai INTEGER NOT NULL DEFAULT 1

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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phieu_nhap(

        id SERIAL PRIMARY KEY,

        ngay DATE,

        khach_hang_id INTEGER NOT NULL,

        CONSTRAINT fk_phieu_nhap_khach_hang
            FOREIGN KEY (khach_hang_id)
            REFERENCES khach_hang(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT

    )
    """)
    cur.execute("""
CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap(

    id SERIAL PRIMARY KEY,

    phieu_nhap_id INTEGER NOT NULL,

    loai_go_id INTEGER NOT NULL,

    so_thanh INTEGER NOT NULL,

    so_luong DOUBLE PRECISION NOT NULL,

    don_gia DOUBLE PRECISION NOT NULL DEFAULT 0,

    thanh_tien DOUBLE PRECISION NOT NULL DEFAULT 0,

    trang_thai VARCHAR(20) NOT NULL DEFAULT 'CHO_HAM',

    ngay_tra DATE,

    CONSTRAINT fk_ctpn_phieu
        FOREIGN KEY (phieu_nhap_id)
        REFERENCES phieu_nhap(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_ctpn_loai_go
        FOREIGN KEY (loai_go_id)
        REFERENCES loai_go(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

)
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ton_kho(

        id SERIAL PRIMARY KEY,

        loai_go_id INTEGER UNIQUE NOT NULL,

        so_thanh INTEGER NOT NULL DEFAULT 0,

        so_m3 DOUBLE PRECISION NOT NULL DEFAULT 0,

        so_kg DOUBLE PRECISION NOT NULL DEFAULT 0,

        CONSTRAINT fk_ton_kho_loai_go
            FOREIGN KEY (loai_go_id)
            REFERENCES loai_go(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ham_say(

        id SERIAL PRIMARY KEY,

        ten_ham VARCHAR(100) NOT NULL UNIQUE

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chi_tiet_ham(

        id SERIAL PRIMARY KEY,

        ham_id INTEGER NOT NULL,

        chi_tiet_phieu_nhap_id INTEGER NOT NULL,

        ngay_vao DATE,

        ngay_ra DATE,

        CONSTRAINT fk_cth_ham
            FOREIGN KEY (ham_id)
            REFERENCES ham_say(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,

        CONSTRAINT fk_cth_ctpn
            FOREIGN KEY (chi_tiet_phieu_nhap_id)
            REFERENCES chi_tiet_phieu_nhap(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cong_no(

        id SERIAL PRIMARY KEY,

        khach_hang_id INTEGER NOT NULL,

        chi_tiet_phieu_nhap_id INTEGER,

        ngay DATE,

        dien_giai TEXT,

        phat_sinh DOUBLE PRECISION NOT NULL DEFAULT 0,

        da_thu DOUBLE PRECISION NOT NULL DEFAULT 0,

        CONSTRAINT fk_cong_no_khach_hang
            FOREIGN KEY (khach_hang_id)
            REFERENCES khach_hang(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,

        CONSTRAINT fk_cong_no_ctpn
            FOREIGN KEY (chi_tiet_phieu_nhap_id)
            REFERENCES chi_tiet_phieu_nhap(id)
            ON UPDATE CASCADE
            ON DELETE SET NULL

    )
    """)
    cur.execute("SELECT COUNT(*) AS count FROM ham_say")

    row = cur.fetchone()

    if row["count"] == 0:

        for i in range(1, 7):

            cur.execute(
                "INSERT INTO ham_say(ten_ham) VALUES(%s)",
                (f"Hầm {i}",)
            )

    conn.commit()

    close_connection(conn)

# =========================
# LOẠI GỖ
# =========================

def lay_ds_loai_go(tu_khoa=""):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM loai_go
        WHERE ma_go LIKE %s
           OR ten_go LIKE %s
        ORDER BY ten_go
    """, (f"%{tu_khoa}%", f"%{tu_khoa}%"))

    data = cur.fetchall()

    close_connection(conn)

    return data


def them_loai_go(ma_go, ten_go, kieu_tinh, day, rong, dai):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO loai_go(

            ma_go,

            ten_go,

            kieu_tinh,

            day,

            rong,

            dai

        )

        VALUES(%s,%s,%s,%s,%s,%s)
    """, (ma_go, ten_go, kieu_tinh, day, rong, dai))

    conn.commit()

    close_connection(conn)

def sua_loai_go(ma_go, ten_go, kieu_tinh, day, rong, dai, id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        UPDATE loai_go

        SET

            ma_go=%s,

            ten_go=%s,

            kieu_tinh=%s,

            day=%s,

            rong=%s,

            dai=%s

        WHERE id=%s
    """, (ma_go, ten_go, kieu_tinh, day, rong, dai, id))

    conn.commit()

    close_connection(conn)


def xoa_loai_go(id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        DELETE FROM loai_go
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
    ngay,
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO phieu_nhap(

            ngay,

            khach_hang_id

        )

        VALUES(%s,%s)

        RETURNING id
    """, (
        ngay,
        khach_hang_id
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
            so_luong,
            don_gia,
            thanh_tien,
            trang_thai
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """, (
        phieu_nhap_id,
        loai_go_id,
        so_thanh,
        so_luong,
        don_gia,
        thanh_tien,
        "CHO_HAM"
    ))

    conn.commit()

    close_connection(conn)

def cap_nhat_ton_kho(
    loai_go_id,
    so_thanh,
    so_m3,
    so_kg
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM ton_kho
        WHERE loai_go_id=%s
    """, (loai_go_id,))

    ton = cur.fetchone()

    if ton is None:

        cur.execute("""
            INSERT INTO ton_kho(

                loai_go_id,

                so_thanh,

                so_m3,

                so_kg

            )

            VALUES(%s,%s,%s,%s)
        """, (
            loai_go_id,
            so_thanh,
            so_m3,
            so_kg
        ))

    else:

        cur.execute("""
            UPDATE ton_kho

            SET

                so_thanh = so_thanh + %s,

                so_m3 = so_m3 + %s,

                so_kg = so_kg + %s

            WHERE loai_go_id=%s
        """, (
            so_thanh,
            so_m3,
            so_kg,
            loai_go_id
        ))

    conn.commit()

    close_connection(conn)

def tru_ton_kho(
    loai_go_id,
    so_thanh,
    so_m3,
    so_kg
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        UPDATE ton_kho

        SET

            so_thanh = so_thanh - %s,

            so_m3 = so_m3 - %s,

            so_kg = so_kg - %s

        WHERE loai_go_id=%s
    """, (
        so_thanh,
        so_m3,
        so_kg,
        loai_go_id
    ))

    conn.commit()

    close_connection(conn)


def lay_ton_kho(trang_thai=None):

    conn = get_connection()
    cur = conn.cursor()

    if trang_thai is None:

        cur.execute("""
            SELECT
                ct.id,
                pn.ngay,
                kh.ten AS khach_hang,
                lg.ma_go,
                lg.ten_go,
                lg.kieu_tinh,
                ct.so_thanh,
                ct.so_luong,
                ct.trang_thai
            FROM chi_tiet_phieu_nhap ct
            JOIN phieu_nhap pn ON ct.phieu_nhap_id = pn.id
            JOIN khach_hang kh ON pn.khach_hang_id = kh.id
            JOIN loai_go lg ON ct.loai_go_id = lg.id
            WHERE ct.trang_thai IN (
                'CHO_HAM',
                'DANG_SAY',
                'CHO_TRA'
            )
            ORDER BY
                pn.ngay,
                kh.ten,
                lg.ten_go
        """)

    else:

        cur.execute("""
            SELECT
                ct.id,
                pn.ngay,
                kh.ten AS khach_hang,
                lg.ma_go,
                lg.ten_go,
                lg.kieu_tinh,
                ct.so_thanh,
                ct.so_luong,
                ct.trang_thai
            FROM chi_tiet_phieu_nhap ct
            JOIN phieu_nhap pn ON ct.phieu_nhap_id = pn.id
            JOIN khach_hang kh ON pn.khach_hang_id = kh.id
            JOIN loai_go lg ON ct.loai_go_id = lg.id
            WHERE ct.trang_thai=%s
            ORDER BY
                pn.ngay,
                kh.ten,
                lg.ten_go
        """, (trang_thai,))

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_ton_theo_loai(loai_go_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT *

        FROM ton_kho

        WHERE loai_go_id=%s
    """, (loai_go_id,))

    data = cur.fetchone()

    close_connection(conn)

    return data


def lay_ds_phieu_nhap():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT

            pn.id,

            pn.ngay,

            kh.ten AS khach_hang

        FROM phieu_nhap pn

        LEFT JOIN khach_hang kh

            ON pn.khach_hang_id = kh.id

        ORDER BY pn.id DESC
    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_chi_tiet_phieu_nhap(phieu_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT
            lg.ma_go,
            lg.ten_go,
            lg.kieu_tinh,
            ct.so_thanh,
            ct.so_luong

        FROM chi_tiet_phieu_nhap ct

        LEFT JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE ct.phieu_nhap_id = %s
    """, (phieu_id,))

    ds = cur.fetchall()

    close_connection(conn)

    return ds


def lay_tong_nhap():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(DISTINCT pn.id) AS so_phieu,

            SUM(
                CASE
                    WHEN lg.kieu_tinh='M3'
                    THEN ct.so_luong
                    ELSE 0
                END
            ) AS tong_m3,

            SUM(
                CASE
                    WHEN lg.kieu_tinh='TRONG_LUONG'
                    THEN ct.so_luong
                    ELSE 0
                END
            ) AS tong_kg,

            SUM(ct.so_thanh) AS tong_thanh

        FROM phieu_nhap pn

        LEFT JOIN chi_tiet_phieu_nhap ct
            ON pn.id = ct.phieu_nhap_id

        LEFT JOIN loai_go lg
            ON ct.loai_go_id = lg.id
    """)

    data = cur.fetchone()

    close_connection(conn)

    return data


def lay_ds_ton_kho():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT

            lg.ma_go,

            lg.ten_go,

            lg.kieu_tinh,

            tk.so_thanh,

            tk.so_m3,

            tk.so_kg

        FROM ton_kho tk

        LEFT JOIN loai_go lg

            ON tk.loai_go_id = lg.id

        ORDER BY lg.ma_go
    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds


def lay_ds_ham():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM ham_say
        ORDER BY id
    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds
def lay_lo_go_chua_vao_ham():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT

            ct.id,

            pn.ngay,

            kh.ten AS khach_hang,

            lg.ma_go,

            lg.ten_go,

            lg.kieu_tinh,

            ct.so_thanh,

            ct.so_luong

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE ct.trang_thai = 'CHO_HAM'

        ORDER BY pn.ngay

    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds


def dua_vao_ham(
    ham_id,
    chi_tiet_id,
    ngay_vao
):
    import time

   
    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chi_tiet_ham(

            ham_id,

            chi_tiet_phieu_nhap_id,

            ngay_vao

        )

        VALUES(%s,%s,%s)

    """, (

        ham_id,

        chi_tiet_id,

        ngay_vao

    ))

    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET trang_thai = 'DANG_SAY'
        WHERE id = %s
    """, (
        chi_tiet_id,
    ))

    conn.commit()

    close_connection(conn)

def lay_ds_trong_ham(ham_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT

            ch.id,

            kh.ten AS khach_hang,

            pn.ngay,

            lg.ma_go,

            lg.ten_go,

            lg.kieu_tinh,

            ct.so_thanh,

            ct.so_luong,

            ch.ngay_vao,

            ch.ngay_ra

        FROM chi_tiet_ham ch

        JOIN chi_tiet_phieu_nhap ct

            ON ch.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn

            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh

            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg

            ON ct.loai_go_id = lg.id

        WHERE ch.ham_id = %s

        AND ch.ngay_ra IS NULL

        ORDER BY ch.ngay_vao

    """, (ham_id,))

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_ds_trong_tat_ca_ham():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ch.ham_id,

            ch.id,

            kh.ten AS khach_hang,

            pn.ngay,

            lg.ma_go,

            lg.ten_go,

            lg.kieu_tinh,

            ct.so_thanh,

            ct.so_luong,

            ch.ngay_vao,

            ch.ngay_ra

        FROM chi_tiet_ham ch

        JOIN chi_tiet_phieu_nhap ct
            ON ch.chi_tiet_phieu_nhap_id = ct.id

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE ch.ngay_ra IS NULL

        ORDER BY ch.ham_id, ch.ngay_vao
    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def ra_ham(
    id_chi_tiet_ham,
    ngay_ra
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT chi_tiet_phieu_nhap_id
        FROM chi_tiet_ham
        WHERE id = %s
    """, (
        id_chi_tiet_ham,
    ))

    row = cur.fetchone()

    if row is None:

        close_connection(conn)

        return

    cur.execute("""
        UPDATE chi_tiet_ham
        SET ngay_ra = %s
        WHERE id = %s
    """, (
        ngay_ra,
        id_chi_tiet_ham
    ))

    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET trang_thai = 'CHO_TRA'
        WHERE id = %s
    """, (
        row["chi_tiet_phieu_nhap_id"],
    ))

    conn.commit()

    close_connection(conn)
def lay_ds_cho_tra():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            ct.id,

            pn.ngay,

            kh.ten AS khach_hang,

            lg.ma_go,

            lg.ten_go,

            lg.kieu_tinh,

            ct.so_thanh,

            ct.so_luong,

            ct.don_gia,

            ct.thanh_tien

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn
            ON ct.phieu_nhap_id = pn.id

        JOIN khach_hang kh
            ON pn.khach_hang_id = kh.id

        JOIN loai_go lg
            ON ct.loai_go_id = lg.id

        WHERE ct.trang_thai='CHO_TRA'

        ORDER BY pn.ngay

    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds


def dua_vao_ham_lai(chi_tiet_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET trang_thai='CHO_HAM'
        WHERE id=%s
    """, (
        chi_tiet_id,
    ))

    conn.commit()

    close_connection(conn)


def tra_khach(chi_tiet_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE chi_tiet_phieu_nhap
        SET
            trang_thai = 'HOAN_TAT',
            ngay_tra = %s
        WHERE id = %s
    """, (
        date.today(),
        chi_tiet_id,
    ))

    conn.commit()

    close_connection(conn)

    them_cong_no(chi_tiet_id)

def them_cong_no(
    chi_tiet_phieu_nhap_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            pn.khach_hang_id,

            ct.ngay_tra,

            lg.ten_go,

            ct.thanh_tien

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn

            ON ct.phieu_nhap_id = pn.id

        JOIN loai_go lg

            ON ct.loai_go_id = lg.id

        WHERE ct.id = %s

    """, (
        chi_tiet_phieu_nhap_id,
    ))

    row = cur.fetchone()

    if row is None:

        close_connection(conn)

        return

    cur.execute("""

        INSERT INTO cong_no(

            khach_hang_id,

            chi_tiet_phieu_nhap_id,

            ngay,

            dien_giai,

            phat_sinh

        )

        VALUES(%s,%s,%s,%s,%s)

    """, (

        row["khach_hang_id"],
        chi_tiet_phieu_nhap_id,
        row["ngay_tra"],
        f"Tiền sấy gỗ {row['ten_go']}",
        row["thanh_tien"]

    ))

    conn.commit()

    close_connection(conn)


def lay_ds_cong_no():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            kh.id,

            kh.ten,

            SUM(phat_sinh) AS tong_no,

            SUM(da_thu) AS tong_thu,

            SUM(phat_sinh-da_thu) AS con_no

        FROM cong_no cn

        JOIN khach_hang kh

            ON cn.khach_hang_id=kh.id

        GROUP BY kh.id, kh.ten

        ORDER BY kh.ten

    """)

    ds = cur.fetchall()

    close_connection(conn)

    return ds

def lay_chi_tiet_cong_no(
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT *

        FROM cong_no

        WHERE khach_hang_id=%s

        ORDER BY id DESC

    """, (
        khach_hang_id,
    ))

    ds = cur.fetchall()

    close_connection(conn)

    return ds


def thu_tien(khach_hang_id, so_tien, ghi_chu, ngay):

    con_no = lay_con_no_khach(khach_hang_id)

    if so_tien <= 0:
        print("Lỗi: Số tiền <= 0")
        return False

    if so_tien > con_no:
        print(f"Lỗi: Tiền thu {so_tien} > Công nợ {con_no}")
        return False

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO cong_no(

            khach_hang_id,

            ngay,

            dien_giai,

            da_thu

        )

        VALUES(%s,%s,%s,%s)

    """, (

        khach_hang_id,

        ngay,

        ghi_chu,

        so_tien

    ))

    conn.commit()

    close_connection(conn)

    return True

def lay_con_no_khach(
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            SUM(phat_sinh-da_thu) AS con_no

        FROM cong_no

        WHERE khach_hang_id=%s

    """, (
        khach_hang_id,
    ))

    row = cur.fetchone()

    close_connection(conn)

    return row["con_no"] or 0


def da_thanh_toan_het(
    khach_hang_id
):

    return lay_con_no_khach(
        khach_hang_id
    ) <= 0


def tong_da_thu(
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            SUM(da_thu) AS tong

        FROM cong_no

        WHERE khach_hang_id = %s

    """, (
        khach_hang_id,
    ))

    row = cur.fetchone()

    close_connection(conn)

    return row["tong"] or 0


def tong_phat_sinh(
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            SUM(phat_sinh) AS tong

        FROM cong_no

        WHERE khach_hang_id = %s

    """, (
        khach_hang_id,
    ))

    row = cur.fetchone()

    close_connection(conn)

    return row["tong"] or 0

def lay_lich_su_khach_hang(
    khach_hang_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            pn.ngay,

            lg.ten_go,

            lg.kieu_tinh,

            ct.so_thanh,

            ct.so_luong,

            ct.don_gia,

            ct.thanh_tien,

            ct.trang_thai

        FROM chi_tiet_phieu_nhap ct

        JOIN phieu_nhap pn

            ON ct.phieu_nhap_id = pn.id

        JOIN loai_go lg

            ON ct.loai_go_id = lg.id

        WHERE pn.khach_hang_id = %s

        ORDER BY pn.ngay DESC,
                 ct.id DESC

    """, (
        khach_hang_id,
    ))

    ds = cur.fetchall()

    close_connection(conn)

    return ds
    
def lay_bao_cao_doanh_thu(
    tu_ngay,
    den_ngay
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            kh.id,
            kh.ten,

            COUNT(
                DISTINCT cn.chi_tiet_phieu_nhap_id
            ) AS so_lo,

            COALESCE(SUM(cn.phat_sinh),0) AS doanh_thu,

            COALESCE(SUM(cn.da_thu),0) AS da_thu,

            COALESCE(SUM(cn.phat_sinh-cn.da_thu),0) AS con_no

        FROM cong_no cn

        JOIN khach_hang kh
            ON kh.id = cn.khach_hang_id

        WHERE cn.ngay BETWEEN %s AND %s

        GROUP BY
            kh.id,
            kh.ten

        ORDER BY
            kh.ten

    """, (
        tu_ngay,
        den_ngay
    ))

    ds = cur.fetchall()

    close_connection(conn)

    return ds