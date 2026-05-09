#!/usr/bin/env python3
import pika
import json
import sys
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
import uuid
import pdfgen
import random
import pdf_server




class RegistrationEvent(BaseModel):
    registration_id: str = str(uuid.uuid4())
    event_name: str
    user_email: EmailStr
    user_name: str
    is_vip: bool = False
    registration_time: str = datetime.now(timezone.utc).isoformat()

def callback(ch, method, properties, body):
    """Обработчик полученных сообщений"""
    try:
        event_data = json.loads(body.decode('utf-8'))
        
        event = RegistrationEvent(**event_data)
        
        print(f"\n{'='*60}")
        print(f"[+] Получено событие:")
        print(f"   Routing Key: {method.routing_key}")
        print(f"   Exchange: {method.exchange}")
        print(f"{'='*60}")
        print(f"[1] Пользователь: {event.user_name}")
        print(f"[2] Email: {event.user_email}")
        print(f"[3] Событие: {event.event_name}")
        print(f"[4] VIP статус: {'Да' if event.is_vip else 'Нет'}")
        
        if not event.is_vip:
            pdfgen.gen_File(event.user_name, event.user_email, event.event_name, event.registration_time, vip=False, seat=random.randint(1, 100))
        else:
            pdfgen.gen_File(event.user_name, event.user_email, event.event_name, event.registration_time, vip=True, seat="VIP Lounge")

        print(f"{'='*60}\n")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError as e:
        print(f"[x] Ошибка парсинга JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"[x] Ошибка обработки события: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        channel = connection.channel()
        
        channel.exchange_declare(
            exchange='event_topic_exchange',
            exchange_type='topic',
            durable=True
        )

        result = channel.queue_declare(
            queue='', 
            exclusive=True,
            auto_delete=True
        )
        queue_name = result.method.queue
        

        routing_keys = [
            'event.registered.vip',     
            'event.registered.regular',  
        ]
        
        for routing_key in routing_keys:
            channel.queue_bind(
                exchange='event_topic_exchange',
                queue=queue_name,
                routing_key=routing_key
            )
            print(f"[x] Привязаны к routing_key: {routing_key}")
        
        print(f"\n[x] Ожидание сообщений в очереди: {queue_name}")
        print("[x] Нажмите CTRL+C для выхода\n")
        

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  
        )
        

        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n\n[x] Программа остановлена пользователем")
        sys.exit(0)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[x] Не удалось подключиться к RabbitMQ: {e}")
        print("Убедитесь, что RabbitMQ запущен: sudo systemctl start rabbitmq")
        sys.exit(1)
    except Exception as e:
        print(f"[x] Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == '__main__':
    import threading
    server_thread = threading.Thread(target=pdf_server.run_server, daemon=True)
    server_thread.start()
    print("[x] PDF сервер запущен на http://localhost:8080")
    main()
