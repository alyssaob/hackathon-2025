import pandas as pd
import plotly.express as px
import os
os.environ["KALEIDO_INSTALL"] = "1"

def make_histogram(data):

    df = pd.DataFrame(data)

    fig = px.histogram(
        df,
        x="amount",
        nbins=5,                # adjust number of bins as you like
        opacity=0.75,
        title="Distribution of Transaction Amounts",
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
    return graph_json

def make_bar_chart(data):
    import pandas as pd
import plotly.express as px

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
        title="Total Spending by Category",
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
    return graph_json
    
def make_pie_chart(data):
    # pie chart
    # build dataframe

    df = pd.DataFrame(data)
    df = df[df["category"] != "Income"]

    # group by category

    grouped = df.groupby("category", as_index=False)["amount"].sum()

    fig = px.pie(
        grouped,
        names="category",
        values="amount",
        title="Share of Total Amount by Category",
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
    return graph_json
    
    # Return URL for client
    file_url = f"/static/output_image.png"

    return file_url
