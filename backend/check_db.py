import sqlite3

def check_database_structure():
    conn = sqlite3.connect('irs.db')
    cursor = conn.cursor()
    
    # Get all columns
    cursor.execute('PRAGMA table_info(nonprofits)')
    columns = cursor.fetchall()
    
    print("All columns in nonprofits table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    print("\n" + "="*50)
    
    # Find time-related fields
    time_keywords = ['year', 'date', 'fiscal', 'period', 'end', 'start']
    time_fields = []
    
    for col in columns:
        col_name = col[1].lower()
        if any(keyword in col_name for keyword in time_keywords):
            time_fields.append(col)
    
    print("Time-related fields:")
    for col in time_fields:
        print(f"  {col[1]} ({col[2]})")
    
    # Check sample data for time fields
    if time_fields:
        print("\nSample data for time fields:")
        sample_fields = [col[1] for col in time_fields[:3]]  # First 3 time fields
        sample_query = f"SELECT {', '.join(sample_fields)} FROM nonprofits LIMIT 5"
        cursor.execute(sample_query)
        sample_data = cursor.fetchall()
        
        for row in sample_data:
            print(f"  {dict(zip(sample_fields, row))}")
    
    # Let's also check for the fiscal year column specifically
    print("\n" + "="*50)
    print("Looking for fiscal year column...")
    
    # Check a few sample rows to see the actual data
    cursor.execute("SELECT * FROM nonprofits LIMIT 3")
    sample_rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    
    print("Sample data from first 3 rows:")
    for i, row in enumerate(sample_rows):
        print(f"\nRow {i+1}:")
        for j, value in enumerate(row):
            if j < 10:  # Show first 10 columns
                print(f"  {column_names[j]}: {value}")
    
    conn.close()





if __name__ == "__main__":
    check_database_structure() 