import json
import os
import secrets
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Создание подключения к базе данных"""
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)

def handler(event: dict, context) -> dict:
    """
    API для работы с ваучерами: получение списка, покупка за токены $SPiTAK.
    При покупке 10% токенов сжигается (burn), остальное списывается с баланса.
    """
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if method == 'GET':
            category = event.get('queryStringParameters', {}).get('category')
            
            if category and category != 'Все':
                cur.execute("""
                    SELECT * FROM vouchers 
                    WHERE is_active = true AND category = %s
                    ORDER BY price_spitak ASC
                """, (category,))
            else:
                cur.execute("""
                    SELECT * FROM vouchers 
                    WHERE is_active = true
                    ORDER BY price_spitak ASC
                """)
            
            vouchers = cur.fetchall()
            
            for v in vouchers:
                v['price_spitak'] = float(v['price_spitak'])
                v['valid_until'] = v['valid_until'].isoformat() if v['valid_until'] else None
                v['created_at'] = v['created_at'].isoformat() if v['created_at'] else None
                v['updated_at'] = v['updated_at'].isoformat() if v['updated_at'] else None
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'vouchers': vouchers}),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            voucher_id = body.get('voucher_id')
            
            if not user_id or not voucher_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'user_id и voucher_id обязательны'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("SELECT balance_spitak FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            if not user:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Пользователь не найден'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("""
                SELECT * FROM vouchers 
                WHERE id = %s AND is_active = true AND remaining_quantity > 0
            """, (voucher_id,))
            voucher = cur.fetchone()
            
            if not voucher:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Ваучер недоступен или закончился'}),
                    'isBase64Encoded': False
                }
            
            price = float(voucher['price_spitak'])
            user_balance = float(user['balance_spitak'])
            
            if user_balance < price:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Недостаточно токенов на балансе'}),
                    'isBase64Encoded': False
                }
            
            burn_amount = price * 0.1
            deduct_amount = price
            
            redemption_code = secrets.token_hex(6).upper()
            qr_code = f"SPITAK-{redemption_code}"
            
            cur.execute("""
                INSERT INTO transactions (user_id, type, amount, currency, status, description, metadata)
                VALUES (%s, 'purchase', %s, 'SPITAK', 'completed', %s, %s)
                RETURNING id
            """, (user_id, price, f'Покупка ваучера {voucher["brand_name"]}', json.dumps({'burn_amount': burn_amount})))
            
            transaction = cur.fetchone()
            
            cur.execute("""
                UPDATE users 
                SET balance_spitak = balance_spitak - %s
                WHERE id = %s
                RETURNING balance_spitak
            """, (deduct_amount, user_id))
            
            updated_user = cur.fetchone()
            
            cur.execute("""
                UPDATE vouchers 
                SET remaining_quantity = remaining_quantity - 1
                WHERE id = %s
            """, (voucher_id,))
            
            cur.execute("""
                INSERT INTO voucher_purchases (user_id, voucher_id, transaction_id, qr_code, redemption_code)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, purchased_at
            """, (user_id, voucher_id, transaction['id'], qr_code, redemption_code))
            
            purchase = cur.fetchone()
            
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'purchase_id': purchase['id'],
                    'qr_code': qr_code,
                    'redemption_code': redemption_code,
                    'burned_spitak': round(burn_amount, 2),
                    'new_balance': float(updated_user['balance_spitak']),
                    'voucher': {
                        'brand': voucher['brand_name'],
                        'discount': voucher['discount_value']
                    }
                }),
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