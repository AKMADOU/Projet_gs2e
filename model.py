from fastapi import FastAPI, HTTPException, Query,Depends,status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime,timedelta
import pymysql
from fastapi import FastAPI, Path
from fastapi_keycloak import FastAPIKeycloak, OIDCUser

app = FastAPI()

idp = FastAPIKeycloak(
    server_url="http://localhost:8080/",
    client_id="tricv",
    client_secret="WFtSMojHAvGfkZP4tNyF458sUYtT5JfK",
    admin_client_secret="WFtSMojHAvGfkZP4tNyF458sUYtT5JfK",
    realm="tricv",
    callback_uri="http://localhost:8081/callback",
)
idp.add_swagger_config(app)

MYSQL_HOST = '10.10.3.56'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'bd_hackathon_modif'

mysql = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    db=MYSQL_DB
)



class Categorie(BaseModel):
    id: Optional[int]
    libelle: str
    is_deleted: Optional[bool]

class Entite(BaseModel):
    id: Optional[int]
    code: str
    libelle: str
    is_deleted: Optional[bool] 

class Fonctionnalite(BaseModel):
    id: Optional[int]
    code: Optional[str]
    nom: str
    is_deleted: Optional[bool]

class Offre(BaseModel):
    nom: str
    date_limite: Optional[datetime]
    chemin_offre: Optional[str]
    entite_id: Optional[int]
    categorie_id: Optional[int]
    date_creation: Optional[datetime]
    date_modification: Optional[datetime]
    is_deleted: Optional[bool]
    user_created: Optional[datetime]
    user_modified: Optional[datetime]
    is_active: Optional[bool]

class Postulant(BaseModel):
    nom: str
    prenoms: str
    email: str
    contacts: Optional[str]
    whatsapp: Optional[str]
    password: str
    is_deleted: Optional[bool]

class PostulantOffre(BaseModel):
    offre_id: int
    postulant_id: int
    chemin_cv: Optional[str]
    chemin_lettre_motivation: Optional[str]

class Role(BaseModel):
    nom: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

class RoleFonctionnalite(BaseModel):
    role_id: int
    fonctionnalite_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

class User(BaseModel):
    login: str
    password: str
    nom: str
    role_id: int
    prenoms: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    civilite: Optional[str] = None
    fonction: Optional[str] = None
    is_aduser: Optional[bool] = True


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# def create_jwt_token(data: dict) -> str:
#        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
# def decode_jwt_token(token: str) -> dict:
#        try:
#            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#            return payload
#        except JWTError:
#            return None
       
@app.get('/categories', tags=["categories"])
def get_categories(page: int = 1, limit: int = 10, order: str = 'DESC'):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT count(*) FROM categorie WHERE is_deleted = 0")
            total_rows = cur.fetchone()[0]

            offset = (page - 1) * limit
            cur.execute(f"SELECT * FROM categorie WHERE is_deleted = 0 ORDER BY id {order} LIMIT {limit} OFFSET {offset}")
            rows = cur.fetchall()

            categories = []
            for row in rows:
                categorie = {
                    'id': int(row[0]),
                    'libelle': row[1],
                    'is_deleted': bool(row[2])
                }
                categories.append(categorie)

        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "items": categories,
            "total": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour récupérer une catégorie par son ID
@app.get('/categories/{id}',tags=["categories"])
def get_categorie(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM categorie WHERE id = %s", (id,))
            categorie = cur.fetchone()

            if not categorie:
                raise HTTPException(status_code=404, detail="Catégorie non trouvée")

            categorie_data = {
                'id': int(categorie[0]),
                'libelle': categorie[1],
                'is_deleted': bool(categorie[2])
            }
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "item": categorie_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour ajouter une nouvelle catégorie
@app.post('/categories',tags=["categories"])
def add_categorie(categorie: Categorie):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO categorie (libelle, is_deleted) VALUES (%s, %s)", (categorie.libelle, categorie.is_deleted))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 201,
                "message": "Catégorie ajoutée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour une catégorie
@app.put('/categories/{id}',tags=["categories"])
def update_categorie(id: int, categorie: Categorie):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE categorie SET libelle = %s, is_deleted = %s WHERE id = %s", (categorie.libelle, categorie.is_deleted, id))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Catégorie mise à jour avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer une catégorie
@app.delete('/categories/{id}',tags=["categories"])
def delete_categorie(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE categorie SET is_deleted = 1 WHERE id = %s", (id,))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Catégorie supprimée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/entites',tags=["entites"])
def get_entites(page: int = 1, limit: int = 10, order: str = 'DESC'):
  
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT count(*) FROM entite WHERE is_deleted = 0")
            total_rows = cur.fetchone()[0]

            offset = (page - 1) * limit
            cur.execute(f"SELECT * FROM entite WHERE is_deleted = 0 ORDER BY id {order} LIMIT {limit} OFFSET {offset}")
            rows = cur.fetchall()

            entites = []
            for row in rows:
                entite = {
                    'id': int(row[0]),
                    'code': row[1],
                    'libelle': row[2],
                    'is_deleted': bool(row[3])
                }
                entites.append(entite)

        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "items": entites,
            "total": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour récupérer une entité par son ID
@app.get('/entites/{id}',tags=["entites"])
def get_entite(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM entite WHERE id = %s", (id,))
            entite = cur.fetchone()

            if not entite:
                raise HTTPException(status_code=404, detail="Entité non trouvée")

            entite_data = {
                'id': int(entite[0]),
                'code': entite[1],
                'libelle': entite[2],
                'is_deleted': bool(entite[3])
            }
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "item": entite_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour ajouter une nouvelle entité
@app.post('/entites',tags=["entites"])
def add_entite(entite: Entite):
    #    , token: str = Depends(oauth2_scheme)
    # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO entite (code, libelle, is_deleted) VALUES (%s, %s, %s)", (entite.code, entite.libelle, entite.is_deleted))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 201,
                "message": "Entité ajoutée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour une entité
@app.put('/entites/{id}',tags=["entites"])
def update_entite(id: int, entite: Entite):
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE entite SET code = %s, libelle = %s, is_deleted = %s WHERE id = %s", (entite.code, entite.libelle, entite.is_deleted, id))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Entité mise à jour avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer une entité
@app.delete('/entites/{id}',tags=["entites"])
def delete_entite(id: int):
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE entite SET is_deleted = 1 WHERE id = %s", (id,))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Entité supprimée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get('/fonctionnalites',tags=["fonctionnalites"])
def get_fonctionnalites(page: int = 1, limit: int = 10, order: str = 'DESC'):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT count(*) FROM fonctionnalite WHERE is_deleted = 0")
            total_rows = cur.fetchone()[0]

            offset = (page - 1) * limit
            cur.execute(f"SELECT * FROM fonctionnalite WHERE is_deleted = 0 ORDER BY id {order} LIMIT {limit} OFFSET {offset}")
            rows = cur.fetchall()

            fonctionnalites = []
            for row in rows:
                fonctionnalite = {
                    'id': int(row[0]),
                    'code': row[1],
                    'nom': row[2],
                    'is_deleted': bool(row[3])
                }
                fonctionnalites.append(fonctionnalite)

        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "items": fonctionnalites,
            "total": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour récupérer une fonctionnalité par son ID
@app.get('/fonctionnalites/{id}',tags=["fonctionnalites"])
def get_fonctionnalite(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM fonctionnalite WHERE id = %s", (id,))
            fonctionnalite = cur.fetchone()

            if not fonctionnalite:
                raise HTTPException(status_code=404, detail="Fonctionnalité non trouvée")

            fonctionnalite_data = {
                'id': int(fonctionnalite[0]),
                'code': fonctionnalite[1],
                'nom': fonctionnalite[2],
                'is_deleted': bool(fonctionnalite[3])
            }
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "item": fonctionnalite_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour ajouter une nouvelle fonctionnalité
@app.post('/fonctionnalites',tags=["fonctionnalites"])
def add_fonctionnalite(fonctionnalite: Fonctionnalite):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO fonctionnalite (code, nom, is_deleted) VALUES (%s, %s, %s)", (fonctionnalite.code, fonctionnalite.nom, fonctionnalite.is_deleted))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 201,
                "message": "Fonctionnalité ajoutée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour une fonctionnalité
@app.put('/fonctionnalites/{id}',tags=["fonctionnalites"])
def update_fonctionnalite(id: int, fonctionnalite: Fonctionnalite):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE fonctionnalite SET code = %s, nom = %s, is_deleted = %s WHERE id = %s", (fonctionnalite.code, fonctionnalite.nom, fonctionnalite.is_deleted, id))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Fonctionnalité mise à jour avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer une fonctionnalité
@app.delete('/fonctionnalites/{id}',tags=["fonctionnalites"])
def delete_fonctionnalite(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE fonctionnalite SET is_deleted = 1 WHERE id = %s", (id,))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Fonctionnalité supprimée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))        


@app.get('/offres', tags=["offres"])
def get_offres(page: int = Query(1, ge=1), limit: int = Query(10, ge=1), order: str = 'DESC'):
    # , token: str = Depends(oauth2_scheme)
    # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")

    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT count(*) FROM offre WHERE is_deleted = 0")
            total_rows = cur.fetchone()[0]

            offset = (page - 1) * limit
            cur.execute(f"SELECT * FROM offre WHERE is_deleted = 0 ORDER BY id {order} LIMIT {limit} OFFSET {offset}")
            rows = cur.fetchall()

            offres = []
            for row in rows:
                offre = {
                    'id': row[0],
                    'nom': row[1],
                    'date_limite': row[2].strftime('%Y-%m-%d') if row[2] else None,
                    'chemin_offre': row[3],
                    'entite_id': row[4],
                    'categorie_id': row[5],
                    'date_creation': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                    'date_modification': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    'is_deleted': bool(row[8]),
                    'user_created': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else None,
                    'user_modified': row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else None,
                    'is_active': bool(row[11])
                }
                offres.append(offre)

        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "items": offres,
            "total": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/offres', tags=["offres"])
def add_offre(offre: Offre):
    # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")

    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO offre (nom, date_limite, chemin_offre, entite_id, categorie_id, date_creation, date_modification, is_deleted, user_created, user_modified, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (offre.nom, offre.date_limite, offre.chemin_offre, offre.entite_id, offre.categorie_id, offre.date_creation, offre.date_modification, offre.is_deleted, offre.user_created, offre.user_modified, offre.is_active))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 201,
                "message": "Offre ajoutée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/offres/{id}', tags=["offres"])
def get_offre(offre_id: int = Path(..., title="ID de l'offre à récupérer")):
    # # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")

    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM offre WHERE id = %s AND is_deleted = 0", (offre_id,))
            offre = cur.fetchone()

            if not offre:
                raise HTTPException(status_code=404, detail="Offre non trouvée")

            offre_data = {
                'id': offre[0],
                'nom': offre[1],
                'date_limite': offre[2].strftime('%Y-%m-%d') if offre[2] else None,
                'chemin_offre': offre[3],
                'entite_id': offre[4],
                'categorie_id': offre[5],
                'date_creation': offre[6].strftime('%Y-%m-%d %H:%M:%S') if offre[6] else None,
                'date_modification': offre[7].strftime('%Y-%m-%d %H:%M:%S') if offre[7] else None,
                'is_deleted': bool(offre[8]),
                'user_created': offre[9].strftime('%Y-%m-%d %H:%M:%S') if offre[9] else None,
                'user_modified': offre[10].strftime('%Y-%m-%d %H:%M:%S') if offre[10] else None,
                'is_active': bool(offre[11])
            }

        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Success"
            },
            "item": offre_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Route pour mettre à jour une offre
@app.put('/offres/{id}', tags=["offres"])
def update_offre(id: int, offre: Offre):
    # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")

    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE offre SET nom = %s, date_limite = %s, chemin_offre = %s, entite_id = %s, categorie_id = %s, date_creation = %s, date_modification = %s, is_deleted = %s, user_created = %s, user_modified = %s, is_active = %s WHERE id = %s", 
                        (offre.nom, offre.date_limite, offre.chemin_offre, offre.entite_id, offre.categorie_id, offre.date_creation, offre.date_modification, offre.is_deleted, offre.user_created, offre.user_modified, offre.is_active, id))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Offre mise à jour avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer une offre
@app.delete('/offres/{id}', tags=["offres"])
def delete_offre(id: int):
    # Vérifier et décoder le token JWT
    # payload = decode_jwt_token(token)
    # if payload is None:
    #     raise HTTPException(status_code=401, detail="Token invalide")

    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE offre SET is_deleted = 1 WHERE id = %s", (id,))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Offre supprimée avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/postulants', response_model=List[Postulant],tags=["postulants"])
def get_all_postulants():
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM postulant")
            rows = cur.fetchall()
            postulants = []
            for row in rows:
                postulant = Postulant(
                    id=row[0],
                    nom=row[1],
                    prenoms=row[2],
                    email=row[3],
                    contacts=row[4],
                    whatsapp=row[5],
                    password=row[6],
                    is_deleted=row[7]
                )
                postulants.append(postulant)
        return postulants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir un postulant par son ID
@app.get('/postulants/{id}', response_model=Postulant,tags=["postulants"])
def get_postulant(postulant_id: int = Path(..., title="ID du postulant à récupérer")):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM postulant WHERE id = %s", (postulant_id,))
            row = cur.fetchone()
            if row:
                return Postulant(
                    id=row[0],
                    nom=row[1],
                    prenoms=row[2],
                    email=row[3],
                    contacts=row[4],
                    whatsapp=row[5],
                    password=row[6],
                    is_deleted=row[7]
                )
            else:
                raise HTTPException(status_code=404, detail="Postulant non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Route pour ajouter un nouveau postulant
@app.post('/postulants',tags=["postulants"])
def add_postulant(postulant: Postulant):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO postulant (nom, prenoms, email, contacts, whatsapp, password, is_deleted) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (postulant.nom, postulant.prenoms, postulant.email, postulant.contacts, postulant.whatsapp, postulant.password, postulant.is_deleted))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 201,
                "message": "Postulant ajouté avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour un postulant
@app.put('/postulants/{id}',tags=["postulants"])
def update_postulant(id: int, postulant: Postulant):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE postulant SET nom = %s, prenoms = %s, email = %s, contacts = %s, whatsapp = %s, password = %s, is_deleted = %s WHERE id = %s", 
                        (postulant.nom, postulant.prenoms, postulant.email, postulant.contacts, postulant.whatsapp, postulant.password, postulant.is_deleted, id))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Postulant mis à jour avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer un postulant
@app.delete('/postulants/{id}',tags=["postulants"])
def delete_postulant(id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE postulant SET is_deleted = 1 WHERE id = %s", (id,))
            mysql.commit()
        return {
            "hasError": False,
            "status": {
                "code": 200,
                "message": "Postulant supprimé avec succès"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/postulant_offres',tags=["postulant_offres"])
def create_postulant_offre(postulant_offre: PostulantOffre):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO postulant_offre (offre_id, postulant_id, chemin_cv, chemin_lettre_motivation) VALUES (%s, %s, %s, %s)",
                        (postulant_offre.offre_id, postulant_offre.postulant_id, postulant_offre.chemin_cv, postulant_offre.chemin_lettre_motivation))
            mysql.commit()
        return {"message": "Postulant offre créé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir tous les enregistrements de postulant_offre
@app.get('/postulant_offres',tags=["postulant_offres"])
def get_all_postulant_offres():
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM postulant_offre")
            results = cur.fetchall()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir un enregistrement spécifique de postulant_offre par son ID
@app.get('/postulant_offres/{offre_id}',tags=["postulant_offres"])
def get_postulant_offre(offre_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM postulant_offre WHERE id = %s", (offre_id,))
            result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Postulant offre non trouvé")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour un enregistrement spécifique de postulant_offre par son ID
@app.put('/postulant_offres/{offre_id}',tags=["postulant_offres"])
def update_postulant_offre(offre_id: int, postulant_offre: PostulantOffre):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE postulant_offre SET offre_id = %s, postulant_id = %s, chemin_cv = %s, chemin_lettre_motivation = %s WHERE id = %s",
                        (postulant_offre.offre_id, postulant_offre.postulant_id, postulant_offre.chemin_cv, postulant_offre.chemin_lettre_motivation, offre_id))
            mysql.commit()
        return {"message": "Postulant offre mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer un enregistrement spécifique de postulant_offre par son ID
@app.delete('/postulant_offres/{offre_id}',tags=["postulant_offres"])
def delete_postulant_offre(offre_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("DELETE FROM postulant_offre WHERE id = %s", (offre_id,))
            mysql.commit()
        return {"message": "Postulant offre supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))      

@app.post('/roles/',tags=["roles"])
def create_role(role: Role):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO role (nom, created_at, updated_at, is_deleted) VALUES (%s, %s, %s, %s)",
                        (role.nom, role.created_at, role.updated_at, role.is_deleted))
            mysql.commit()
        return {"message": "Rôle créé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir tous les rôles
@app.get('/roles/',tags=["roles"])
def read_roles():
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM role WHERE is_deleted = 0")
            roles = cur.fetchall()
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir un rôle spécifique par son ID
@app.get('/roles/{id}',tags=["roles"])
def read_role(role_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM role WHERE id = %s", (role_id,))
            role = cur.fetchone()
        if not role:
            raise HTTPException(status_code=404, detail="Rôle non trouvé")
        return role
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour un rôle spécifique par son ID
@app.put('/roles/{id}',tags=["roles"])
def update_role(role_id: int, role: Role):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE role SET nom = %s, updated_at = %s WHERE id = %s",
                        (role.nom, datetime.now(), role_id))
            mysql.commit()
        return {"message": "Rôle mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer un rôle spécifique par son ID
@app.delete('/roles/{id}',tags=["roles"])
def delete_role(role_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE role SET is_deleted = 1 WHERE id = %s", (role_id,))
            mysql.commit()
        return {"message": "Rôle supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

@app.post('/role_fonctionnalites/',tags=["role_fonctionnalites"])
def create_role_fonctionnalite(role_fonctionnalite: RoleFonctionnalite):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO role_fonctionnalite (role_id, fonctionnalite_id, created_at, updated_at, is_deleted) VALUES (%s, %s, %s, %s, %s)",
                        (role_fonctionnalite.role_id, role_fonctionnalite.fonctionnalite_id, role_fonctionnalite.created_at, role_fonctionnalite.updated_at, role_fonctionnalite.is_deleted))
            mysql.commit()
        return {"message": "Relation entre rôle et fonctionnalité créée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir toutes les relations entre rôles et fonctionnalités
@app.get('/role_fonctionnalites/',tags=["role_fonctionnalites"])
def read_role_fonctionnalites( ):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM role_fonctionnalite WHERE is_deleted = 0")
            role_fonctionnalites = cur.fetchall()
        return role_fonctionnalites
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir une relation spécifique entre rôle et fonctionnalité par son ID
@app.get('/role_fonctionnalites/{id}',tags=["role_fonctionnalites"])
def read_role_fonctionnalite(role_fonctionnalite_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM role_fonctionnalite WHERE id = %s", (role_fonctionnalite_id,))
            role_fonctionnalite = cur.fetchone()
        if not role_fonctionnalite:
            raise HTTPException(status_code=404, detail="Relation rôle-fonctionnalité non trouvée")
        return role_fonctionnalite
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour une relation spécifique entre rôle et fonctionnalité par son ID
@app.put('/role_fonctionnalites/{id}',tags=["role_fonctionnalites"])
def update_role_fonctionnalite(role_fonctionnalite_id: int, role_fonctionnalite: RoleFonctionnalite):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE role_fonctionnalite SET role_id = %s, fonctionnalite_id = %s, updated_at = %s WHERE id = %s",
                        (role_fonctionnalite.role_id, role_fonctionnalite.fonctionnalite_id, datetime.now(), role_fonctionnalite_id))
            mysql.commit()
        return {"message": "Relation rôle-fonctionnalité mise à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer une relation spécifique entre rôle et fonctionnalité par son ID
@app.delete('/role_fonctionnalites/{id}',tags=["role_fonctionnalites"])
def delete_role_fonctionnalite(role_fonctionnalite_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE role_fonctionnalite SET is_deleted = 1 WHERE id = %s", (role_fonctionnalite_id,))
            mysql.commit()
        return {"message": "Relation rôle-fonctionnalité supprimée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/users/',tags=["users"])
def create_user(user: User):
    try:
        with mysql.cursor() as cur:
            cur.execute("INSERT INTO user (login, password, nom, role_id, prenoms, email, telephone, civilite, fonction, is_aduser) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (user.login, user.password, user.nom, user.role_id, user.prenoms, user.email, user.telephone, user.civilite, user.fonction, user.is_aduser))
            mysql.commit()
        return {"message": "Utilisateur créé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir tous les utilisateurs
@app.get('/users/',tags=["users"])
def read_users():
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour obtenir un utilisateur spécifique par son ID
@app.get('/users/{id}',tags=["users"])
def read_user(user_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour mettre à jour un utilisateur spécifique par son ID
@app.put('/users/{id}',tags=["users"])
def update_user(user_id: int, user: User):
    try:
        with mysql.cursor() as cur:
            cur.execute("UPDATE user SET login = %s, password = %s, nom = %s, role_id = %s, prenoms = %s, email = %s, telephone = %s, civilite = %s, fonction = %s, is_aduser = %s WHERE id = %s",
                        (user.login, user.password, user.nom, user.role_id, user.prenoms, user.email, user.telephone, user.civilite, user.fonction, user.is_aduser, user_id))
            mysql.commit()
        return {"message": "Utilisateur mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route pour supprimer un utilisateur spécifique par son ID
@app.delete('/users/{id}',tags=["users"])
def delete_user(user_id: int):
    try:
        with mysql.cursor() as cur:
            cur.execute("DELETE FROM user WHERE id = %s", (user_id,))
            mysql.commit()
        return {"message": "Utilisateur supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
