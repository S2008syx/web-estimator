import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def millions(x, pos):
    return f'${int(x):,}'


formatter = FuncFormatter(millions)

# 【1、标题和用户输入 & 401K计算】
st.title("Retirement Asset Planning Simulator (By Sibo Song)")
calculation_mode = st.radio(
    "Choose how you want to calculate your 401k amount",
    ("Use the 401K preloaded calculator", "I know my 401k amount and prefer to enter it manually")
)

retire_display = st.empty()

if calculation_mode == "Use the 401K preloaded calculator":
    st.subheader("401k Growth During Accumulation Period")
    interest1 = st.number_input(
        "401k Annual Compounded Return Rate(During Accumulation Period)",
        value=1.06,
        help="Expected compounded annual return rate of 401k during the accumulation phase.(No capital gains tax for 401K, it is regard as ordinary income tax)"
    )
    GroR = interest1
    retire = 0
    years = st.slider("Number of Years Contributing to 401k", 0, 50, 25,
                      help="For example: If you have contributed to your 401k for 15 years, set this to 15.")

    store = st.number_input("Annual 401k Contribution Before Retirement($)", value=30000,
                            help="Enter the amount you contribute annually to your 401k before retirement. Enter 0 if not applicable.")
    for _ in range(years):
        retire = (retire + store) * GroR


else:
    st.subheader("Manual 401k Input")
    user_input = st.number_input(
        "Current 401k Balance (for users no longer contributing) ($)",
        value=500000,
        help="If you already know your current 401k balance and are no longer making contributions"
    )

    retire = user_input

retire_display.markdown(f"**Total Amount of 401k：** `${retire:,.0f}`")
st.subheader("🎯 Retirement Planning Begins")

prin = st.number_input("Total Other Assets at Retirement (excluding 401k)", value=2000000,
                       help="Includes bank savings, stocks, real estate, and other liquid assets.")

spend = st.number_input("Estimated Annual Retirement Expenses", value=100000,
                        help="Adjust based on your lifestyle and region.")

portion = st.slider("Proportion of Expenses Covered by 401k", 0.0, 1.0, 0.5,
                    help="For example: 0.5 means 50% of annual spending comes from your 401k, the rest from other assets.")

interest = st.number_input("Expected Annual Return Rate (After Tax) During Retirement", value=1.06,
                           help="Expected average investment return rate for both 401k and other assets after retirement. Enter 1.06 for 6%.")

inflation = st.number_input("Expected Annual Inflation Rate", value=1.03,
                            help="Affects growth in annual expenses. Enter 1.03 for 3% inflation.")

# 【二、退休模拟】
x = 1
totalP = 0
prin_balance = prin
retire_balance = retire
retire_list = []
totalP_list = []
list_tax = []
Total_spend_list = []


def get_tax_rate(retire_spend):
    if 0 <= retire_spend <= 11925:
        return 1 - 0.10
    elif 11926 <= retire_spend <= 48475:
        return 1 - ((11925 / retire_spend) * 0.10 + (1 - 11925 / retire_spend) * 0.12)
    elif 48476 <= retire_spend <= 103350:
        return 1 - ((48475 / retire_spend) * 0.108 + (1 - 48475 / retire_spend) * 0.22)
    elif 103351 <= retire_spend <= 197300:
        return 1 - ((103350 / retire_spend) * 0.1708 + (1 - 103350 / retire_spend) * 0.24)
    elif 197301 <= retire_spend <= 250525:
        return 1 - ((197300 / retire_spend) * 0.2037 + (1 - 197300 / retire_spend) * 0.32)
    elif 250526 <= retire_spend <= 626350:
        return 1 - ((250525 / retire_spend) * 0.2248 + (1 - 250525 / retire_spend) * 0.35)
    elif retire_spend > 626350:
        return 1 - ((626350 / retire_spend) * 0.3014 + (1 - 626350 / retire_spend) * 0.37)
    else:
        raise ValueError("retire_spend not within a valid range")


while x < 51:
    Total_spend = spend * (inflation ** x)
    retire_spend = spend * (inflation ** x) * portion
    tax = get_tax_rate(retire_spend)
    list_tax.append(1 - tax)
    Total_spend_list.append(Total_spend)
    prin_balance = prin_balance * interest - spend * (inflation ** x) * (1 - portion)
    retire_balance = retire_balance * interest - retire_spend / tax
    totalP = prin_balance + retire_balance

    retire_list.append(retire_balance)
    totalP_list.append(totalP)

    if retire_balance <= 0:
        totalP -= (1 - list_tax[-1]) * retire_list[-1]
        break
    x += 1

# 【三、401k耗尽后，仅用本金模拟】
while x < 51:
    totalP = totalP * interest - spend * (inflation ** x)
    totalP_list.append(totalP)
    Total_spend_list.append(spend * (inflation ** x))
    if totalP <= 0:
        break
    x += 1

# 【四、图表显示】
# total principal graph
fig, ax = plt.subplots()
ax.plot(range(1, len(totalP_list) + 1), totalP_list, label="Total Assets ($)")
ax.set_title("Total Retirement Asset Over Time")
for yearx in [1, 10, 20, 30, 40, 50]:
    if yearx <= len(totalP_list):
        value = totalP_list[yearx - 1]
        ax.annotate(f"${value:,.0f}", (yearx, value),
                    textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8)
        ax.plot(yearx, value, 'ko')

ax.set_xlabel("Years After Retirement")
ax.set_ylabel("Total Assets ($)")
plt.gca().yaxis.set_major_formatter(formatter)
ax.legend()
ax.grid(True)
st.pyplot(fig)
# tax rates graph
fig, ax = plt.subplots()
ax.plot(range(1, len(list_tax) + 1), list_tax, label="Tax Rates of 401k")
ax.set_title("401k Tax Rate Over the Years")
for yearx in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
    if yearx <= len(list_tax):
        value = list_tax[yearx - 1]
        ax.annotate(f"{value * 100:.1f}%", (yearx, value),
                    textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8)
        ax.plot(yearx, value, 'ko')

ax.set_xlabel("Years After Retirement")
ax.set_ylabel("Annual Tax Rate")
ax.legend()
ax.grid(True)
st.pyplot(fig)
# annually spending graph
fig, ax = plt.subplots()
ax.plot(range(1, len(Total_spend_list) + 1), Total_spend_list, label="Annual Spending")
ax.set_title("Annual Spending After Retirement")
for yearx in [1, 10, 20, 30, 40, 50]:
    if yearx <= len(Total_spend_list):
        value = Total_spend_list[yearx - 1]
        ax.annotate(f"${value:,.0f}", (yearx, value),
                    textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8)
        ax.plot(yearx, value, 'ko')

ax.set_xlabel("Years After Retirement")
ax.set_ylabel("Annual Spending")
plt.gca().yaxis.set_major_formatter(formatter)
ax.legend()
ax.grid(True)
st.pyplot(fig)

# 【五、附加说明】
st.success(
    "Note: This simulator assumes zero state tax. Federal taxes are calculated based on marginal brackets and only apply to 401k withdrawals. Other assets are assumed to be tax-free.")