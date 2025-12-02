#!/usr/bin/env python3
"""
데이터베이스 조회 스크립트
사용법: python view_db.py
"""
import sqlite3
from datetime import datetime
from tabulate import tabulate

def format_datetime(dt_str):
    """날짜 시간 포맷팅"""
    if dt_str:
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str
    return ""

def view_users(conn):
    """사용자 조회"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, role, wallet_address, kyc_verified, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        headers = ["ID", "Email", "Role", "Wallet", "KYC", "Created"]
        table_data = []
        for row in rows:
            table_data.append([
                str(row[0])[:8] + "...",
                row[1],
                row[2],
                row[3][:10] + "..." if row[3] else "None",
                "✓" if row[4] else "✗",
                format_datetime(row[5])
            ])
        print("\n📋 사용자 목록")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("\n📋 사용자 없음")

def view_events(conn):
    """이벤트 조회"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, status, price_wei, sold_tickets, max_tickets, 
               event_id_onchain, created_at 
        FROM events 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        headers = ["ID", "Name", "Status", "Price (wei)", "Sold/Max", "Onchain ID", "Created"]
        table_data = []
        for row in rows:
            table_data.append([
                str(row[0])[:8] + "...",
                row[1][:30] + "..." if len(row[1]) > 30 else row[1],
                row[2],
                f"{row[3]:,}" if row[3] else "0",
                f"{row[4]}/{row[5]}",
                row[6] if row[6] else "None",
                format_datetime(row[7])
            ])
        print("\n🎫 이벤트 목록")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("\n🎫 이벤트 없음")

def view_tickets(conn):
    """티켓 조회"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, token_id, owner_address, status, purchase_price_wei, created_at 
        FROM tickets 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        headers = ["ID", "Token ID", "Owner", "Status", "Price (wei)", "Created"]
        table_data = []
        for row in rows:
            table_data.append([
                str(row[0])[:8] + "...",
                row[1],
                row[2][:10] + "..." if row[2] else "None",
                row[3],
                f"{row[4]:,}" if row[4] else "0",
                format_datetime(row[5])
            ])
        print("\n🎟️  티켓 목록")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("\n🎟️  티켓 없음")

def view_stats(conn):
    """통계 정보"""
    cursor = conn.cursor()
    
    stats = {}
    
    # 사용자 수
    cursor.execute("SELECT COUNT(*) FROM users")
    stats['users'] = cursor.fetchone()[0]
    
    # 이벤트 수
    cursor.execute("SELECT COUNT(*) FROM events")
    stats['events'] = cursor.fetchone()[0]
    
    # 티켓 수
    cursor.execute("SELECT COUNT(*) FROM tickets")
    stats['tickets'] = cursor.fetchone()[0]
    
    # 재판매 수
    cursor.execute("SELECT COUNT(*) FROM resales")
    stats['resales'] = cursor.fetchone()[0]
    
    # 환불 요청 수
    cursor.execute("SELECT COUNT(*) FROM refund_requests")
    stats['refunds'] = cursor.fetchone()[0]
    
    print("\n📊 데이터베이스 통계")
    print(f"  사용자: {stats['users']}명")
    print(f"  이벤트: {stats['events']}개")
    print(f"  티켓: {stats['tickets']}개")
    print(f"  재판매: {stats['resales']}개")
    print(f"  환불 요청: {stats['refunds']}개")

def main():
    """메인 함수"""
    db_path = "ticketing.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        print("=" * 60)
        print("🗄️  블록체인 티켓팅 데이터베이스 조회")
        print("=" * 60)
        
        view_stats(conn)
        view_users(conn)
        view_events(conn)
        view_tickets(conn)
        
        print("\n" + "=" * 60)
        print("✅ 조회 완료")
        print("=" * 60)
        
        conn.close()
        
    except FileNotFoundError:
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()

