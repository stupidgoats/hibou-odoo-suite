# Part of Hibou Suite Professional. See LICENSE_PROFESSIONAL file for full copyright and licensing details.

from .general import _state_applies


def mn_minnesota_state_income_withholding(payslip, categories, worked_days, inputs):
    """
    Returns SIT eligible wage and rate.
    WAGE = GROSS + DED_FIT_EXEMPT

    :return: result, result_rate (wage, percent)
    """
    state_code = 'MN'
    if not _state_applies(payslip, state_code):
        return 0.0, 0.0

    filing_status = payslip.dict.contract_id.us_payroll_config_value('mn_w4mn_sit_filing_status')
    if not filing_status:
        return 0.0, 0.0

    # Determine Wage
    wage = categories.GROSS + categories.DED_FIT_EXEMPT
    pay_periods = payslip.dict.get_pay_periods_in_year()
    additional = payslip.dict.contract_id.us_payroll_config_value('state_income_tax_additional_withholding')
    sit_tax_rate = payslip.dict.rule_parameter('us_mn_sit_tax_rate')[filing_status]
    allowances_rate = payslip.dict.rule_parameter('us_mn_sit_allowances_rate')
    allowances = payslip.dict.contract_id.us_payroll_config_value('mn_w4mn_sit_allowances')
    if wage == 0.0:
        return 0.0, 0.0

    taxable_income = (wage * pay_periods) - (allowances * allowances_rate)
    withholding = 0.0
    for row in sit_tax_rate:
        cap, subtract_amt, rate, flat_fee = row
        cap = float(cap)
        if cap > taxable_income:
            withholding = ((rate / 100.00) * (taxable_income - subtract_amt)) + flat_fee
            break
    withholding = round(withholding / pay_periods)
    if withholding < 0.0:
        withholding = 0.0
    withholding += additional
    return wage, -((withholding / wage) * 100.0)
