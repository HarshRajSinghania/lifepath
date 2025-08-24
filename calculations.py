import math

def calculate_loan_payment(principal, annual_rate=0.05, years=10):
    """
    Calculate monthly loan payment using standard loan formula.
    
    Args:
        principal (float): Total loan amount
        annual_rate (float): Annual interest rate (default 5%)
        years (int): Loan term in years (default 10)
    
    Returns:
        float: Monthly payment amount
    """
    if principal <= 0:
        return 0
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(payment, 2)

def calculate_annual_dream_cost(dream_data):
    """
    Calculate total annual cost of dream lifestyle.
    
    Args:
        dream_data (dict): Dictionary containing monthly costs
    
    Returns:
        float: Total annual cost
    """
    monthly_total = (
        dream_data.get('housing_cost', 0) +
        dream_data.get('transportation_cost', 0) +
        dream_data.get('food_cost', 0) +
        dream_data.get('entertainment_cost', 0) +
        dream_data.get('other_cost', 0)
    )
    return monthly_total * 12

def calculate_monthly_expenses_total(expenses_list):
    """
    Calculate total monthly expenses from expenses list.
    
    Args:
        expenses_list (list): List of expense dictionaries
    
    Returns:
        float: Total monthly expenses
    """
    return sum(expense.get('amount', 0) for expense in expenses_list)

def calculate_financial_gap(user_profile):
    """
    Calculate the gap between dream cost and projected income after expenses.
    
    Args:
        user_profile (dict): Complete user profile data
    
    Returns:
        dict: Financial analysis results
    """
    dream = user_profile.get('dream', {})
    reality = user_profile.get('reality', {})
    path = user_profile.get('path', {})
    
    # Annual costs
    annual_dream_cost = dream.get('annual_dream_cost', 0)
    projected_salary = path.get('projected_starting_salary', 0)
    
    # Monthly calculations
    monthly_dream_cost = annual_dream_cost / 12
    monthly_salary = projected_salary / 12
    monthly_expenses = calculate_monthly_expenses_total(reality.get('expenses', []))
    monthly_loan_payment = path.get('estimated_loan_payment', 0)
    
    # Available income after current expenses and loans
    available_monthly = monthly_salary - monthly_expenses - monthly_loan_payment
    
    # Gap calculation
    monthly_gap = monthly_dream_cost - available_monthly
    annual_gap = monthly_gap * 12
    
    # Percentage calculations
    dream_affordability = (available_monthly / monthly_dream_cost * 100) if monthly_dream_cost > 0 else 100
    loan_burden = (monthly_loan_payment / monthly_salary * 100) if monthly_salary > 0 else 0
    
    return {
        'monthly_dream_cost': round(monthly_dream_cost, 2),
        'monthly_salary': round(monthly_salary, 2),
        'monthly_expenses': round(monthly_expenses, 2),
        'monthly_loan_payment': round(monthly_loan_payment, 2),
        'available_monthly': round(available_monthly, 2),
        'monthly_gap': round(monthly_gap, 2),
        'annual_gap': round(annual_gap, 2),
        'dream_affordability': round(dream_affordability, 1),
        'loan_burden': round(loan_burden, 1),
        'can_afford_dream': monthly_gap <= 0
    }

def calculate_savings_needed(target_amount, monthly_contribution, annual_return=0.07):
    """
    Calculate how long it takes to save a target amount with compound interest.
    
    Args:
        target_amount (float): Target savings goal
        monthly_contribution (float): Monthly savings amount
        annual_return (float): Expected annual return rate (default 7%)
    
    Returns:
        dict: Savings timeline analysis
    """
    if monthly_contribution <= 0:
        return {'months': float('inf'), 'years': float('inf')}
    
    monthly_rate = annual_return / 12
    
    if monthly_rate == 0:
        months = target_amount / monthly_contribution
    else:
        # Future value of annuity formula solved for time
        months = math.log(1 + (target_amount * monthly_rate) / monthly_contribution) / math.log(1 + monthly_rate)
    
    return {
        'months': round(months, 1),
        'years': round(months / 12, 1),
        'total_contributed': round(monthly_contribution * months, 2),
        'interest_earned': round(target_amount - (monthly_contribution * months), 2)
    }
