import pandas as pd
import plotly.express as px
import os
os.environ["KALEIDO_INSTALL"] = "1"

def make_histogram(data):

    df = pd.DataFrame(data)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df["amount"] = df["amount"].abs()  # optional if you want positive spending 

    fig = px.histogram(
        df,
        x="amount",
        nbins=5,                # adjust number of bins as you like
        opacity=0.75,
        labels={"amount": "Amount ($)"}

    )

    # Format axis ticks as currency and tidy layout

    fig.update_layout(
        xaxis_tickprefix="$",
        xaxis_tickformat=",.2f",
        yaxis_title="Count",
        legend_title_text="Category",
        margin=dict(l=40, r=20, t=60, b=60)
    )
    
    graph_json = fig.to_json()
    fig.show()
    return graph_json

# def make_bar_chart(data):
#     import pandas as pd
# import plotly.express as px

def make_bar_chart(data):
    df = pd.DataFrame(data)

    # Exclude income
    df = df[df["category"] != "Income"]

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    # Convert expenses to positive values
    df["amount"] = df["amount"].abs()

    # Group by category
    grouped = df.groupby("category", as_index=False)["amount"].sum()

    # Plot
    fig = px.bar(
        grouped,
        x="category",
        y="amount",
        labels={"category": "Category", "amount": "Amount ($)"}
    )

    # Format bars and labels
    fig.update_traces(
        texttemplate="$%{y:,.2f}",
        textposition="inside"
    )

    fig.update_layout(
        xaxis_type="category",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.2f",
        bargap=0.3,
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        margin=dict(l=40, r=20, t=60, b=80)
    )

    graph_json = fig.to_json()
    fig.show()
    return graph_json
    
def make_pie_chart(data):
    # pie chart
    # build dataframe

    df = pd.DataFrame(data)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df = df[df["category"] != "Income"]

    # group by category

    grouped = df.groupby("category", as_index=False)["amount"].sum()

    fig = px.pie(
        grouped,
        names="category",
        values="amount",
        hole=0.0
    )

    # Show category, dollar, and percent on labels/hover

    fig.update_traces(

        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )

    fig.update_layout(margin=dict(l=40, r=40, t=60, b=40))

    graph_json = fig.to_json()
    fig.show()
    return graph_json
    
