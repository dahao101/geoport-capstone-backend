def extract_report(report_id, report_data):
    return {
        "report_id": report_id,
        "type": report_data.get('TypeOfReport', 'N/A'),
        "status": report_data.get('status', 'Unknown'),
        "reference": report_data.get('reference', 'N/A'),
        "reporter": report_data.get('reporter', 'Unknown'),
        "image": report_data.get('image', ''),
        "severity": report_data.get('Severity', False),
        "date_reported": report_data.get('DateAndTime', 'Unknown'),
        "location": report_data.get('location', {}),
        "passable": report_data.get('passable', False),
        "latitude": report_data.get('location', {}).get('latitude'),
        "longitude": report_data.get('location', {}).get('longitude'),
        "version": report_data.get('version', 1)
    }
