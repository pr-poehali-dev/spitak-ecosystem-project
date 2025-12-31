import json
import os
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Создание подключения к базе данных"""
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)

def handler(event: dict, context) -> dict:
    """
    API для трекинга шагов и начисления токенов SPiTAK.
    Принимает количество шагов от пользователя, сохраняет в БД и начисляет токены.
    Формула: 1000 шагов = 1 $SPiTAK (с учётом boost-множителя).
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
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            steps_count = body.get('steps_count', 0)
            distance_km = body.get('distance_km', 0.0)
            calories = body.get('calories_burned', 0)
            active_minutes = body.get('active_minutes', 0)
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'user_id обязателен'}),
                    'isBase64Encoded': False
                }
            
            today = date.today()
            
            cur.execute("""
                SELECT balance_spitak FROM users WHERE id = %s
            """, (user_id,))
            user = cur.fetchone()
            
            if not user:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Пользователь не найден'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("""
                SELECT boost_multiplier FROM staking 
                WHERE user_id = %s AND is_active = true
                ORDER BY staked_at DESC LIMIT 1
            """, (user_id,))
            staking = cur.fetchone()
            boost_multiplier = staking['boost_multiplier'] if staking else 1.0
            
            spitak_earned = (steps_count / 1000) * boost_multiplier
            
            cur.execute("""
                INSERT INTO daily_steps (user_id, date, steps_count, distance_km, calories_burned, active_minutes, spitak_earned, boost_multiplier)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, date) DO UPDATE SET
                    steps_count = daily_steps.steps_count + EXCLUDED.steps_count,
                    distance_km = daily_steps.distance_km + EXCLUDED.distance_km,
                    calories_burned = daily_steps.calories_burned + EXCLUDED.calories_burned,
                    active_minutes = daily_steps.active_minutes + EXCLUDED.active_minutes,
                    spitak_earned = daily_steps.spitak_earned + EXCLUDED.spitak_earned,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING spitak_earned
            """, (user_id, today, steps_count, distance_km, calories, active_minutes, spitak_earned, boost_multiplier))
            
            result = cur.fetchone()
            total_spitak_today = result['spitak_earned']
            
            cur.execute("""
                UPDATE users 
                SET balance_spitak = balance_spitak + %s,
                    total_earned = total_earned + %s,
                    balance_steps = balance_steps + %s,
                    last_activity_date = %s
                WHERE id = %s
                RETURNING balance_spitak, balance_steps
            """, (spitak_earned, spitak_earned, steps_count, today, user_id))
            
            updated_user = cur.fetchone()
            
            cur.execute("""
                INSERT INTO transactions (user_id, type, amount, currency, status, description)
                VALUES (%s, 'mint', %s, 'SPITAK', 'completed', %s)
            """, (user_id, spitak_earned, f'Начислено за {steps_count} шагов'))
            
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'steps_added': steps_count,
                    'spitak_earned': round(spitak_earned, 2),
                    'total_spitak_today': round(total_spitak_today, 2),
                    'balance_spitak': float(updated_user['balance_spitak']),
                    'balance_steps': updated_user['balance_steps'],
                    'boost_multiplier': boost_multiplier
                }),
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
                SELECT date, steps_count, spitak_earned, boost_multiplier
                FROM daily_steps
                WHERE user_id = %s
                ORDER BY date DESC
                LIMIT 30
            """, (user_id,))
            
            history = cur.fetchall()
            
            for record in history:
                record['date'] = record['date'].isoformat()
                record['spitak_earned'] = float(record['spitak_earned'])
                record['boost_multiplier'] = float(record['boost_multiplier'])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'history': history}),
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
