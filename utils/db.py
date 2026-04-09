from utils.supabase_client import supabase, int_to_uuid

def save_complaint(data: dict):
    """Inserts a new complaint record into the Supabase 'complaints' table."""
    response = supabase.table("complaints").insert(data).execute()
    return response.data

def fetch_all_complaints():
    """Retrieves all complaints, ordered strictly by newest first."""
    response = supabase.table("complaints").select("*").order("created_at", desc=True).execute()
    return response.data

def fetch_user_complaints(user_id):
    """Retrieves complaints localized/associated with a specific user profile ID."""
    response = supabase.table("complaints").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data

def update_complaint_status(complaint_id: int, status: str, assigned_officer_id: int = None, repair_status: str = None):
    """Safely transitions state and handles assignment assignments metadata."""
    update_data = {"status": status}
    
    if assigned_officer_id is not None:
        update_data["assigned_officer"] = int_to_uuid(assigned_officer_id)  # Maps automatically to UUID format
    if repair_status is not None:
        update_data["repair_status"] = repair_status
        
    response = supabase.table("complaints").update(update_data).eq("id", complaint_id).execute()
    return response.data
