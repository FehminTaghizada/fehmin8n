from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# 1) Giriş qapısı
engine = create_engine("postgresql+psycopg2://postgres:12345@localhost:5432/postgres")

# 2) Cədvəlin təsviri
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(200))


# 3) Cədvəli database-də yarat (varsa, toxunmur)
Base.metadata.create_all(engine)

# 4) Session fabriki
Session = sessionmaker(bind=engine)
session = Session()


def istifadecileri_goster(siyahi):
    """Cədvəl şəklində çap — Addım 3-ün eyni formatı."""
    print(f"\n{'ID':<5} | {'Ad':<20} | {'Email'}")
    print("-" * 50)
    if not siyahi:
        print("Siyahı boşdur.")
        return
    for user in siyahi:
        print(f"{user.id:<5} | {user.name:<20} | {user.email}")
    print("-" * 50)
    print(f"Cəmi: {len(siyahi)}")


def email_duzgundur(email):
    return "@" in email and "." in email.split("@")[-1]


# --- Addım 1: dərs nümunəsi — Kamran ---
if not session.query(User).filter_by(email="kamran@mail.com").first():
    session.add(User(name="Kamran", email="kamran@mail.com"))
    session.commit()
    print("Kamran əlavə olundu.")
else:
    print("Kamran artıq cədvəldə var.")


while True:
    print("\n===== İstifadəçi Dəftəri =====")
    print("1. Yeni istifadəçi əlavə et")
    print("2. Hamısını göstər")
    print("3. Ada görə axtar")
    print("4. Email dəyiş")
    print("5. İstifadəçini sil")
    print("0. Çıxış")

    secim = input("Seçiminiz: ").strip()

    # --- Addım 2: input() ilə yaz ---
    if secim == "1":
        ad = input("Ad: ").strip()
        email = input("Email: ").strip()

        if not ad or not email:
            print("Ad və email boş ola bilməz.")
        elif not email_duzgundur(email):
            print("Email düzgün deyil (nümunə: ad@mail.com).")
        elif session.query(User).filter_by(email=email).first():
            print("Bu email artıq mövcuddur.")
        else:
            session.add(User(name=ad, email=email))
            session.commit()
            print(f"{ad} əlavə olundu!")

    # --- Addım 3: bütün istifadəçiləri oxu ---
    elif secim == "2":
        users = session.query(User).order_by(User.id).all()
        istifadecileri_goster(users)

    elif secim == "3":
        axtar = input("Axtardığınız ad: ").strip()
        if axtar:
            netice = (
                session.query(User)
                .filter(User.name.ilike(f"%{axtar}%"))
                .order_by(User.name)
                .all()
            )
            istifadecileri_goster(netice)
        else:
            print("Axtarış boş ola bilməz.")

    elif secim == "4":
        istifadecileri_goster(session.query(User).order_by(User.id).all())
        try:
            user_id = int(input("Dəyişmək istədiyiniz ID: "))
        except ValueError:
            print("ID rəqəm olmalıdır.")
            continue

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            print("Belə ID yoxdur.")
        else:
            yeni_email = input(f"Yeni email ({user.email}): ").strip()
            if not email_duzgundur(yeni_email):
                print("Email düzgün deyil.")
            elif session.query(User).filter_by(email=yeni_email).first():
                print("Bu email artıq mövcuddur.")
            else:
                user.email = yeni_email
                session.commit()
                print(f"{user.name} üçün email yeniləndi.")

    elif secim == "5":
        istifadecileri_goster(session.query(User).order_by(User.id).all())
        try:
            user_id = int(input("Silmək istədiyiniz ID: "))
        except ValueError:
            print("ID rəqəm olmalıdır.")
            continue

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            print("Belə ID yoxdur.")
        else:
            tesdiq = input(f"{user.name} silinsin? (he/yox): ").strip().lower()
            if tesdiq == "he":
                session.delete(user)
                session.commit()
                print("Silindi.")
            else:
                print("Ləğv olundu.")

    elif secim == "0":
        print("Bağlanır...")
        break

    else:
        print("Yanlış seçim. 0–5 arası yazın.")

session.close()
