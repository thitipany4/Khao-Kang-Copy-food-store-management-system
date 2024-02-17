def calculator(orb):
    sum_expenses =0
    sum_income =0

    for i in orb:
        if i.transaction_type == 'income':
            sum_income +=i.total_price
        if i.transaction_type == 'expenses':
            sum_expenses +=i.total_price

    return sum_expenses,sum_income