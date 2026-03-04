import streamlit as st
import mysql.connector
import pandas as pd

st.set_page_config(page_title=" Smart Logistics Dashboard", layout="wide", initial_sidebar_state="expanded")

# DB connection #
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="091267",
        database="smart_logistics"
    )

# Fetch data from DB #
def fetch_data(query,params=None):
    conn = get_connection()
    df = pd.read_sql(query,conn,params=params)
    conn.close()
    return df

# SIDEBAR NAVIGATION #
st.sidebar.title("Smart Logistics")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Shipments",
        "Advanced Analytics"
    ]
)

# DASHBOARD #
 
if page == "Dashboard":
    st.title("Operations Dashboard")
    st.markdown("All systems nominal")
    st.divider()

    # Sidebar Controls #
    dashboard_sections = st.sidebar.multiselect(
        "Dashboard Sections",
        [
            "KPIs",
            "Shipment Volume",
            "Status Distribution",
            "Recent Shipments"
        ],
        default=[
            "KPIs"
        ]
    )
    # Query 1: Total Shipments
    total_df = fetch_data("SELECT COUNT(*) FROM shipments;")
    total_shipments = int(total_df.iloc[0, 0])
    # Query 2: Delivered %
    delivered_df = fetch_data("""
    SELECT ROUND(
        SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(*), 2
    )
    FROM shipments;
    """)
    delivered_percent = delivered_df.iloc[0, 0]
    # Query 3: In Transit %
    in_transit_df = fetch_data("""
    SELECT ROUND(
        SUM(CASE WHEN status = 'In Transit' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(*), 2
    )
    FROM shipments;
    """)
    in_transit_percent = in_transit_df.iloc[0, 0]
    # Query 4: Cancelled %
    cancelled_df = fetch_data("""
    SELECT ROUND(
        SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(*), 2
    )
    FROM shipments;
    """)
    cancelled_percent = cancelled_df.iloc[0, 0]
    # Query 5: Average Delivery Time
    avg_time_df = fetch_data("""
        SELECT 
            ROUND(AVG(DATEDIFF(delivery_date, order_date)), 2) AS avg_delivery_days
        FROM shipments
        WHERE status = 'Delivered'
        AND delivery_date IS NOT NULL;
    """)
    avg_delivery_time = avg_time_df.iloc[0, 0]
    # Query 6: Total Operational Cost
    cost_df = fetch_data("""
        SELECT 
            ROUND(SUM(fuel_cost + labor_cost + misc_cost), 2) AS total_cost
        FROM costs;
    """)
    total_operational_cost = cost_df.iloc[0, 0]
# KPI Metrics #
    if "KPIs" in dashboard_sections:

        row1_col1, row1_col2, row1_col3 = st.columns(3)

        row1_col1.metric("📦 Total Shipments", total_shipments)
        row1_col2.metric("✅ Delivered %", f"{delivered_percent}%")
        row1_col3.metric("🚚 In Transit %", f"{in_transit_percent}%")

        row2_col1, row2_col2, row2_col3 = st.columns(3)

        row2_col1.metric("❌ Cancelled %", f"{cancelled_percent}%")
        row2_col2.metric("⏱ Avg Delivery Time", f"{avg_delivery_time} days")
        row2_col3.metric("💰 Total Operational Cost", f"₹ {total_operational_cost:,.2f}")


    st.divider()

# Shipment Volume (Last 7 Days) #

    if "Shipment Volume" in dashboard_sections:

        volume_df = fetch_data("""
            SELECT 
                order_date,
                COUNT(*) AS total_shipments,
                SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_shipments
            FROM shipments
            GROUP BY order_date
            ORDER BY order_date DESC
            LIMIT 7;
            """)

        volume_df = volume_df.sort_values("order_date")
        volume_df = volume_df.set_index("order_date")

        st.subheader("📦 Shipment Volume - Last 7 Days")
        st.bar_chart(volume_df)
        st.divider()

# Shipment Status Distribution #
    if "Status Distribution" in dashboard_sections:
        status_df = fetch_data("""
            SELECT status, COUNT(*) AS total
            FROM shipments
            GROUP BY status;
        """)

        status_df = status_df.set_index("status")

        st.subheader("📊 Shipment Status Distribution")
        st.bar_chart(status_df)

#RECENT SHIPMENTS #
    if "Recent Shipments" in dashboard_sections:

        recent_df = fetch_data("""
            SELECT shipment_id, origin, destination, status, delivery_date
            FROM shipments
            ORDER BY order_date DESC
            LIMIT 10;
        """)

        st.subheader("Recent Shipments")

        if not recent_df.empty:
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No shipments available.")
# SHIPMENTS #

elif page == "Shipments":
    st.title("Shipments")
    st.markdown("Enter your tracking number to get real-time updates on your delivery.")
    st.divider()

# Filters #
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Delivered", "In Transit", "Cancelled", "Pending"]
        )

    with col2:
        origin_df = fetch_data("SELECT DISTINCT origin FROM shipments")
        origin_options = ["All"] + origin_df["origin"].tolist()
        origin_filter = st.selectbox("Origin", origin_options)

    with col3:
        destination_df = fetch_data("SELECT DISTINCT destination FROM shipments")
        destination_options = ["All"] + destination_df["destination"].tolist()
        destination_filter = st.selectbox("Destination", destination_options)


    # Second row of filters
    col4, col5 = st.columns(2)

    with col4:
        courier_df = fetch_data("SELECT courier_id FROM courier_staff")
        courier_options = ["All"] + courier_df["courier_id"].tolist()
        courier_filter = st.selectbox("Courier", courier_options)

    with col5:
        date_range = st.date_input(
            "Order Date Range",
            []
        )

    # Search box
    search_id = st.text_input("Search by Shipment ID")

# BUILD QUERY FOR DROPDOWN #

    base_query = "FROM shipments WHERE 1=1"

    # Status
    if status_filter != "All":
        base_query += f" AND status = '{status_filter}'"

    # Origin
    if origin_filter != "All":
        base_query += f" AND origin = '{origin_filter}'"

    # Destination
    if destination_filter != "All":
        base_query += f" AND destination = '{destination_filter}'"

    # Courier
    if courier_filter != "All":
        base_query += f" AND courier_id = '{courier_filter}'"

    # Search
    if search_id:
        base_query += f" AND shipment_id LIKE '%{search_id}%'"

    # Date Range
    if len(date_range) == 2:
        start_date = date_range[0]
        end_date = date_range[1]
        base_query += f" AND order_date BETWEEN '{start_date}' AND '{end_date}'"

    dropdown_query = f"""
        SELECT shipment_id
        {base_query}
        ORDER BY order_date DESC
        LIMIT 200
    """

    shipment_list_df = fetch_data(dropdown_query)

    st.divider()

# DROPDOWN SELECTOR #

    if not shipment_list_df.empty:

        selected_shipment = st.selectbox(
            "Select Shipment",
            shipment_list_df["shipment_id"]
        )

        # SHIPMENT DETAILS #

        details_query = f"""
            SELECT *
            FROM shipments
            WHERE shipment_id = '{selected_shipment}'
        """

        details_df = fetch_data(details_query)

        st.subheader("Shipment Details")

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"**Shipment ID**  \n{details_df.iloc[0]['shipment_id']}")
        col2.markdown(f"**Status**  \n{details_df.iloc[0]['status']}")
        col3.markdown(f"**Weight**  \n{details_df.iloc[0]['weight']} kg")

        col4, col5, col6 = st.columns(3)

        col4.markdown(f"**Origin**  \n{details_df.iloc[0]['origin']}")
        col5.markdown(f"**Destination**  \n{details_df.iloc[0]['destination']}")
        col6.markdown(f"**Courier ID**  \n{details_df.iloc[0]['courier_id']}")

        # TRACKING TIMELINE #

        tracking_query = f"""
            SELECT status, timestamp
            FROM shipment_tracking
            WHERE shipment_id = '{selected_shipment}'
            ORDER BY timestamp ASC
        """

        tracking_df = fetch_data(tracking_query)

        st.subheader("Tracking Timeline")

        if not tracking_df.empty:

            current_status = details_df.iloc[0]["status"]

            for i, row in tracking_df.iterrows():

                if row["status"] == current_status:
                    circle = "🟢"
                else:
                    circle = "●"

                st.markdown(f"{circle} **{row['status']}**")

                st.markdown(
                    f"<span style='color:gray; font-size:15px'>{row['timestamp']}</span>",
                    unsafe_allow_html=True
                )

                if i < len(tracking_df) - 1:
                    st.markdown("│")
                    st.markdown("│")

        else:
            st.info("No tracking history available.")

    else:
        st.warning("No shipments match selected filters.")
# ADVANCE ANALYTICS #
elif page == "Advanced Analytics":

    st.title("Advanced Logistics Analytics")
    st.caption("Comprehensive operational analytics for performance evaluation.")
    st.divider()

    analytics_sections = st.sidebar.multiselect(
        "Analytics Modules",
        [
            "Delivery Performance",
            "Courier Performance",
            "Cost Analytics",
            "Cancellation Analysis",
            "Warehouse Insights"
        ],
        default=[
            "Delivery Performance"
        ]
    )

# 1 DELIVERY PERFORMANCE INSIGHTS #
    if "Delivery Performance" in analytics_sections:
        
        st.subheader("Delivery Performance Insights")

        # Average delivery time per route
        route_avg_query = """
            SELECT 
                r.origin,
                r.destination,
                r.distance_km,
                ROUND(AVG(DATEDIFF(s.delivery_date, s.order_date)), 2) AS avg_delivery_days
            FROM shipments s
            JOIN routes r 
                ON s.origin = r.origin 
                AND s.destination = r.destination
            WHERE s.status = 'Delivered'
            GROUP BY r.origin, r.destination, r.distance_km
            ORDER BY avg_delivery_days DESC
            LIMIT 10
        """

        route_avg_df = fetch_data(route_avg_query)

        st.write("Most Delayed Routes")
        st.dataframe(route_avg_df, hide_index=True, use_container_width=True)

        # Delivery time vs distance
        st.write("Delivery Time vs Distance")
        st.scatter_chart(
            route_avg_df.set_index("distance_km")["avg_delivery_days"]
        )
        st.markdown("### Route Efficiency (Days per KM)")

        route_efficiency_df = fetch_data("""
            SELECT 
                r.origin,
                r.destination,
                r.distance_km,
                ROUND(AVG(DATEDIFF(s.delivery_date, s.order_date)),2) AS avg_delivery_days,
                ROUND(
                    AVG(DATEDIFF(s.delivery_date, s.order_date)) / r.distance_km,
                    4
                ) AS days_per_km
            FROM shipments s
            JOIN routes r
                ON s.origin = r.origin 
                AND s.destination = r.destination
            WHERE s.status = 'Delivered'
            GROUP BY r.origin, r.destination, r.distance_km
            ORDER BY days_per_km DESC
            LIMIT 10;
        """)

        if not route_efficiency_df.empty:
            st.dataframe(route_efficiency_df, hide_index=True)
        else:
            st.info("No route efficiency data available.")

# 2 COURIER PERFORMANCE #
    if "Courier Performance" in analytics_sections:
        st.divider()
        st.subheader("Courier Performance")

        courier_perf_query = """
            SELECT 
                s.courier_id,
                COUNT(*) AS total_shipments,
                ROUND(
                    SUM(CASE 
                        WHEN s.status = 'Delivered' 
                        AND DATEDIFF(s.delivery_date, s.order_date) <= 3 
                        THEN 1 ELSE 0 END
                    ) / COUNT(*) * 100,
                    2
                ) AS on_time_rate,
                ROUND(AVG(c.rating), 2) AS avg_rating
            FROM shipments s
            JOIN courier_staff c 
                ON s.courier_id = c.courier_id
            GROUP BY s.courier_id
            ORDER BY on_time_rate DESC
            LIMIT 10
        """

        courier_perf_df = fetch_data(courier_perf_query)

        st.dataframe(courier_perf_df, hide_index=True, use_container_width=True)

        st.write("On-Time Delivery %")
        st.bar_chart(courier_perf_df.set_index("courier_id")["on_time_rate"])

        st.write("Average Rating Comparison")
        st.bar_chart(courier_perf_df.set_index("courier_id")["avg_rating"])

# 3 COST ANALYTICS #
    if "Cost Analytics" in analytics_sections:
        st.divider()
        st.subheader("Cost Analytics")

        route_cost_query = """
            SELECT 
                s.origin,
                s.destination,
                ROUND(SUM(c.fuel_cost + c.labor_cost + c.misc_cost), 2) AS total_route_cost
            FROM shipments s
            JOIN costs c ON s.shipment_id = c.shipment_id
            GROUP BY s.origin, s.destination
            ORDER BY total_route_cost DESC
            LIMIT 10
        """

        route_cost_df = fetch_data(route_cost_query)

        st.write("Cost per Route")
        st.dataframe(route_cost_df, hide_index=True, use_container_width=True)

        # Fuel vs labor %
        cost_breakdown_query = """
            SELECT 
                ROUND(SUM(fuel_cost),2) AS fuel,
                ROUND(SUM(labor_cost),2) AS labor,
                ROUND(SUM(misc_cost),2) AS misc
            FROM costs
        """

        cost_breakdown_df = fetch_data(cost_breakdown_query)

        st.write("Fuel vs Labor Contribution")
        st.bar_chart(cost_breakdown_df)

        # High-cost shipments
        high_cost_query = """
            SELECT 
                shipment_id,
                ROUND(fuel_cost + labor_cost + misc_cost,2) AS total_cost
            FROM costs
            ORDER BY total_cost DESC
            LIMIT 10
        """

        high_cost_df = fetch_data(high_cost_query)

        st.write("High-Cost Shipments")
        st.dataframe(high_cost_df, hide_index=True)

        st.markdown("### Cost vs Weight Analysis")
        cost_weight_df = fetch_data("""
            SELECT 
                s.weight,
                (c.fuel_cost + c.labor_cost + c.misc_cost) AS total_cost
            FROM shipments s
            JOIN costs c ON s.shipment_id = c.shipment_id
            WHERE s.weight IS NOT NULL
            LIMIT 500;
        """)

        if not cost_weight_df.empty:
            st.scatter_chart(cost_weight_df)
        else:
            st.info("No cost-weight data available.")

# 4 CANCELLATION ANALYSIS #
    if "Cancellation Analysis" in analytics_sections:
        st.divider()
        st.subheader("Cancellation Analysis")

        cancel_origin_query = """
            SELECT 
                origin,
                COUNT(*) AS cancellations
            FROM shipments
            WHERE status = 'Cancelled'
            GROUP BY origin
            ORDER BY cancellations DESC
            LIMIT 10
        """

        cancel_origin_df = fetch_data(cancel_origin_query)

        st.write("Cancellation by Origin")
        st.bar_chart(cancel_origin_df.set_index("origin"))

        # Cancellation by courier
        cancel_courier_query = """
            SELECT 
                courier_id,
                COUNT(*) AS cancellations
            FROM shipments
            WHERE status = 'Cancelled'
            GROUP BY courier_id
            ORDER BY cancellations DESC
            LIMIT 10
        """

        cancel_courier_df = fetch_data(cancel_courier_query)

        st.write("Cancellation by Courier")
        st.bar_chart(cancel_courier_df.set_index("courier_id"))

        # Time-to-cancellation
        cancel_time_query = """
            SELECT 
                ROUND(AVG(DATEDIFF(delivery_date, order_date)),2) AS avg_time_to_cancel
            FROM shipments
            WHERE status = 'Cancelled'
        """

        cancel_time_df = fetch_data(cancel_time_query)

        st.metric(
            "Average Time to Cancellation (Days)",
            cancel_time_df.iloc[0]["avg_time_to_cancel"]
        )

# 5 WAREHOUSE INSIGHTS #
    if "Warehouse Insights" in analytics_sections:
        st.divider()
        st.subheader("Warehouse Insights")
# 1 Warehouse Capacity Comparison
        warehouse_capacity_df = fetch_data("""
            SELECT city, capacity
            FROM warehouses
            ORDER BY capacity DESC;
        """)

        if not warehouse_capacity_df.empty:

            warehouse_capacity_df = warehouse_capacity_df.set_index("city")

            st.markdown("### Warehouse Capacity Comparison")
            st.bar_chart(warehouse_capacity_df)

        else:
            st.info("No warehouse data available.")
            
# 2 High-Traffic Warehouse Cities #
        traffic_df = fetch_data("""
            SELECT 
                origin AS city,
                COUNT(*) AS shipment_volume
            FROM shipments
            GROUP BY origin
            ORDER BY shipment_volume DESC
            LIMIT 10;
        """)

        if not traffic_df.empty:

            traffic_df = traffic_df.set_index("city")

            st.markdown("### High-Traffic Warehouse Cities")
            st.bar_chart(traffic_df)

        else:
            st.info("No shipment traffic data available.")




