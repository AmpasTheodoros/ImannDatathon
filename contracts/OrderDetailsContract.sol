@app.route('/handle_order', methods=['POST'])
def handle_order():
    # Extract order details
    # ...
    
    # Process each order detail
    for detail in order_details:
        # Extract and/or generate contract terms using AI
        # ...
        
        # Create a record on the blockchain
        receipt = create_blockchain_record(order_id, product_id, product_details)
        # Log receipt or handle confirmation
        # ...
    
    return 'Order processed'