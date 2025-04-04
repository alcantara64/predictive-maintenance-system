# from fastapi import Depends, HTTPException, status
# from auth.routes import get_current_user

# def super_admin_only(current_user=Depends(get_current_user)):
#     if current_user["role"] != "super_admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Super admin access required"
#         )
#     return current_user
