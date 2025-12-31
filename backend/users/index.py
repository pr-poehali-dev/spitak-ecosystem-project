import json
import os
import secrets
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Создание подключения к базе данных"""
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)

def generate_referral_code():
    """Генерация уникального реферального кода"""
    return secrets.token_urlsafe(6).upper()[:8]

def handler(event: dict, context) -> dict:
    """
    API для работы с пользователями: регистрация, получение профиля, обновление данных.
    При регистрации автоматически создаётся реферальный код.
    """
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            phone_number = body.get('phone_number')
            full_name = body.get('full_name')
            district = body.get('district')
            referred_by_code = body.get('referral_code')
            
            if not phone_number:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'phone_number обязателен'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
            existing = cur.fetchone()
            
            if existing:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Пользователь с таким номером уже существует'}),
                    'isBase64Encoded': False
                }
            
            referral_code = generate_referral_code()
            referred_by_id = None
            
            if referred_by_code:
                cur.execute("SELECT id FROM users WHERE referral_code = %s", (referred_by_code,))
                referrer = cur.fetchone()
                if referrer:
                    referred_by_id = referrer['id']
            
            cur.execute("""
                INSERT INTO users (phone_number, full_name, district, referral_code, referred_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, phone_number, full_name, referral_code, balance_spitak, balance_steps, created_at
            """, (phone_number, full_name, district, referral_code, referred_by_id))
            
            user = cur.fetchone()
            
            if referred_by_id:
                bonus_amount = 5.0
                
                cur.execute("""
                    UPDATE users SET balance_spitak = balance_spitak + %s
                    WHERE id = %s
                """, (bonus_amount, referred_by_id))
                
                cur.execute("""
                    INSERT INTO referrals (referrer_id, referred_user_id, bonus_spitak)
                    VALUES (%s, %s, %s)
                """, (referred_by_id, user['id'], bonus_amount))
            
            conn.commit()
            
            user['balance_spitak'] = float(user['balance_spitak'])
            user['created_at'] = user['created_at'].isoformat()
            
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'user': user}),
                'isBase64Encoded': False
            }
        
        elif method == 'GET':
            user_id = event.get('queryStringParameters', {}).get('user_id')
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'user_id обязателен'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("""
                SELECT id, phone_number, full_name, username, wallet_address, referral_code,
                       is_kyc_verified, kyc_tier, balance_steps, balance_spitak, total_earned,
                       streak_days, last_activity_date, district, avatar_url, created_at
                FROM users WHERE id = %s
            """, (user_id,))
            
            user = cur.fetchone()
            
            if not user:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Пользователь не найден'}),
                    'isBase64Encoded': False
                }
            
            user['balance_spitak'] = float(user['balance_spitak'])
            user['total_earned'] = float(user['total_earned'])
            user['last_activity_date'] = user['last_activity_date'].isoformat() if user['last_activity_date'] else None
            user['created_at'] = user['created_at'].isoformat()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'user': user}),
                'isBase64Encoded': False
            }
        
        elif method == 'PUT':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'user_id обязателен'}),
                    'isBase64Encoded': False
                }
            
            updates = []
            params = []
            
            if 'full_name' in body:
                updates.append("full_name = %s")
                params.append(body['full_name'])
            if 'username' in body:
                updates.append("username = %s")
                params.append(body['username'])
            if 'district' in body:
                updates.append("district = %s")
                params.append(body['district'])
            if 'avatar_url' in body:
                updates.append("avatar_url = %s")
                params.append(body['avatar_url'])
            
            if not updates:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Нет данных для обновления'}),
                    'isBase64Encoded': False
                }
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING *"
            
            cur.execute(query, params)
            user = cur.fetchone()
            conn.commit()
            
            user['balance_spitak'] = float(user['balance_spitak'])
            user['total_earned'] = float(user['total_earned'])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'user': user}),
                'isBase64Encoded': False
            }
        
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Метод не поддерживается'}),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
    finally:
        cur.close()
        conn.close()
