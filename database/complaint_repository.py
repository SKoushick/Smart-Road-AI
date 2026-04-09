import os
import sys
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.supabase_client import supabase, int_to_uuid, uuid_to_int

def _map_row(d: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamically map Supabase columns back to legacy UI columns so the dashboards don't crash."""
    if d:
        d["date"] = d.get("created_at", "")
        d["assigned_officer_id"] = uuid_to_int(d.get("assigned_officer", None))
    return d

# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

def insert_complaint(data: Dict[str, Any]) -> int:
    try:
        response = supabase.table("complaints").insert(data).execute()
        return response.data[0]["id"] if response.data else 0
    except Exception:
        return 0

# ──────────────────────────────────────────────
# FETCH
# ──────────────────────────────────────────────

def fetch_all_complaints() -> List[Dict[str, Any]]:
    response = supabase.table("complaints").select("*").order("created_at", desc=True).execute()
    return [_map_row(d) for d in (response.data or [])]

def fetch_complaint_by_id(complaint_id: int) -> Optional[Dict[str, Any]]:
    response = supabase.table("complaints").select("*").eq("id", complaint_id).execute()
    return _map_row(response.data[0]) if response.data else None

def fetch_complaints_by_status(status: str) -> List[Dict[str, Any]]:
    response = supabase.table("complaints").select("*").eq("status", status).order("created_at", desc=True).execute()
    return [_map_row(d) for d in (response.data or [])]

def fetch_complaints_by_officer(officer_id: int) -> List[Dict[str, Any]]:
    uid = int_to_uuid(officer_id)
    response = supabase.table("complaints").select("*").eq("assigned_officer", uid).order("created_at", desc=True).execute()
    return [_map_row(d) for d in (response.data or [])]

# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def update_complaint_status(complaint_id: int, new_status: str, resolved_by: str = "", notes: str = "") -> bool:
    try:
        supabase.table("complaints").update({
            "status": new_status,
            "resolved_by": resolved_by,
            "notes": notes
        }).eq("id", complaint_id).execute()
        return True
    except Exception:
        return False

def update_complaint_assignment(complaint_id: int, officer_id: int, assigned_time: str) -> bool:
    uid = int_to_uuid(officer_id)
    try:
        # Try full update including status 'In Progress' (to satisfy Supabase CHECK constraints)
        supabase.table("complaints").update({
            "assigned_officer": uid,
            "assigned_time": assigned_time,
            "status": "In Progress",
            "repair_status": "Pending"
        }).eq("id", complaint_id).execute()
        return True
    except Exception:
        try:
            # Fallback: Stripping optional columns if they don't exist in Supabase
            supabase.table("complaints").update({
                "assigned_officer": uid,
                "status": "In Progress"
            }).eq("id", complaint_id).execute()
            return True
        except Exception as fallback_err:
            print("CRITICAL DISPATCH FAILURE:", fallback_err)
            return False

def update_complaint_repair_status(complaint_id: int, new_status: str, repair_status: str) -> bool:
    try:
        supabase.table("complaints").update({
            "status": new_status,
            "repair_status": repair_status
        }).eq("id", complaint_id).execute()
        return True
    except Exception:
        try:
            # Fallback: Just update 'status' if 'repair_status' column doesn't exist
            supabase.table("complaints").update({
                "status": new_status
            }).eq("id", complaint_id).execute()
            return True
        except Exception:
            return False

# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def delete_complaint(complaint_id: int) -> bool:
    try:
        supabase.table("complaints").delete().eq("id", complaint_id).execute()
        return True
    except Exception:
        return False

# ──────────────────────────────────────────────
# ANALYTICS HELPERS
# ──────────────────────────────────────────────

def fetch_severity_counts() -> Dict[str, int]:
    data = fetch_all_complaints()
    counts = {}
    for row in data:
        s = row.get("severity_level")
        counts[s] = counts.get(s, 0) + 1
    return counts

def fetch_status_counts() -> Dict[str, int]:
    data = fetch_all_complaints()
    counts = {}
    for row in data:
        s = row.get("status")
        counts[s] = counts.get(s, 0) + 1
    return counts

def fetch_monthly_counts() -> List[Dict[str, Any]]:
    data = fetch_all_complaints()
    months = {}
    for row in data:
        date_str = row.get("date")
        if date_str and len(date_str) >= 7:
            m = date_str[:7]
            months[m] = months.get(m, 0) + 1
    return [{"month": k, "cnt": v} for k, v in sorted(months.items())]

def fetch_location_counts() -> List[Dict[str, Any]]:
    data = fetch_all_complaints()
    locs = {}
    for row in data:
        loc = row.get("location_name")
        if loc:
            locs[loc] = locs.get(loc, 0) + 1
    sorted_locs = sorted(locs.items(), key=lambda x: x[1], reverse=True)[:15]
    return [{"location_name": k, "cnt": v} for k, v in sorted_locs]
