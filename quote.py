TAX_RATE = 0.25  # Swedish MOMS

def calculate_quote(selected_services):
    subtotal = sum(s.price for s in selected_services)
    moms     = subtotal * TAX_RATE
    total    = subtotal + moms
    return {
        'subtotal': subtotal,
        'moms':     moms,
        'total':    total,
        'lines':    selected_services
    }