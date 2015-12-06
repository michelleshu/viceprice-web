conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
hits = list(conn.get_all_hits())
for hit in hits:
    conn.disable_hit(hit.HITId)