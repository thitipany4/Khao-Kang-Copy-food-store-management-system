def calculator(orb,text=None):
    list_income = []
    list_expenses =[]
    list_leftover =[]
    for t in orb:
            if t.transaction_type == 'expenses':
                    list_expenses.append(t)
                #     print(t,t.transaction_type)

            elif t.transaction_type == 'income':
                    list_income.append(t)
                #     print(t,t.transaction_type)

            else:
                 list_leftover.append(t)

    sum_expenses = sum([t.price * t.amount for t in list_expenses])
    sum_income = sum([t.price * t.amount for t in list_income])
    if text =="show_note":
        return sum_expenses,sum_income,list_expenses,list_income,list_leftover
    else:
        return sum_expenses,sum_income