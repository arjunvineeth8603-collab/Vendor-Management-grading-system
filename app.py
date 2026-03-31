import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Logistics Vendor Governance", layout="wide", page_icon="🚢")

METRICS = [
    "Accuracy", 
    "Crisis Response", 
    "Resilience/RTC", 
    "Cost/Rates", 
    "Credit Facility"
]

page_bg_img = '''
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-color: rgba(240, 242, 246, 0.95);
    background-blend-mode: overlay;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


def calculate_grade(score):
    if score >= 8.5: return 'A (Strategic)'
    elif score >= 7.0: return 'B (Preferred)'
    elif score >= 5.0: return 'C (Needs Improvement)'
    else: return 'D (Terminate/Replace)'


if 'categories' not in st.session_state:
    st.session_state.categories = ['Transport', 'Shipping Line', 'Airlines', 'CFS', 'CHA']

# Setup Vendors Memory (Now including KYC fields)
if 'vendors' not in st.session_state:
    initial_data = {
        'Vendor ID': ['V001', 'V002', 'V003'],
        'Name': ['SafeExpress Logistics', 'Conex', 'Impulse'],
        'Category': ['Transport', 'CFS', 'CHA'],
        'Status': ['Active', 'Active', 'Under Review'],
        'GSTIN': ['27AADCS1461E1Z2', '07AAAAA0000A1Z5', '29BBBBB1111B1Z1'],
        'PAN': ['AADCS1461E', 'AAAAA0000A', 'BBBBB1111B'],
        'Bank Account': ['000123456789', '000987654321', '000555666777'],
        'IFSC Code': ['HDFC0000001', 'SBIN0000002', 'ICIC0000003']
    }
    
    initial_data[METRICS[0]] = [9, 8, 5]
    initial_data[METRICS[1]] = [8, 9, 6]
    initial_data[METRICS[2]] = [9, 7, 5]
    initial_data[METRICS[3]] = [10, 8, 4]
    initial_data[METRICS[4]] = [8, 9, 5]
    
    initial_data['Final Score (out of 10)'] = [8.8, 8.2, 5.0]
    initial_data['Final Grade'] = ['A (Strategic)', 'B (Preferred)', 'C (Needs Improvement)']
    
    st.session_state.vendors = pd.DataFrame(initial_data)

st.sidebar.image("logo.png", use_container_width=True) 


st.sidebar.title("Vendor Management System")
page = st.sidebar.radio("Go to:", ["Dashboard", "Vendor Directory", "Onboarding & Settings", "Vendor Grading System"])


if page == "Dashboard":
    st.title("Governance Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Partners", len(st.session_state.vendors))
    
    top_vendors = len(st.session_state.vendors[st.session_state.vendors['Final Grade'].str.contains('A|B')])
    col2.metric("Top Performers (A/B)", top_vendors)
    col3.metric("Avg. Network Score (/10)", round(st.session_state.vendors['Final Score (out of 10)'].mean(), 1))

    fig = px.pie(st.session_state.vendors, names='Final Grade', title="Vendor Grading Distribution", hole=0.4)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)") 
    st.plotly_chart(fig, use_container_width=True)


elif page == "Vendor Directory":
    st.title("Registered Vendors")
    
    search = st.text_input("Search by Vendor Name or GSTIN")
    
   
    filtered_df = st.session_state.vendors[
        st.session_state.vendors['Name'].str.contains(search, case=False) |
        st.session_state.vendors['GSTIN'].str.contains(search, case=False)
    ]
    
    display_cols = ['Vendor ID', 'Name', 'Category', 'Status', 'GSTIN', 'PAN', 'Final Score (out of 10)', 'Final Grade']
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)


elif page == "Onboarding & Settings":
    st.title("Onboarding & System Settings")
    
    tab1, tab2 = st.tabs(["Add New Vendor", "Manage Categories"])
    
   
    with tab1:
        st.write("### Register a New Logistics Partner")
        with st.form("add_vendor_form"):
            st.write("#### 1. Basic Details")
            col_a, col_b = st.columns(2)
            with col_a:
                new_v_id = st.text_input("Vendor ID (e.g., V004)")
                new_v_name = st.text_input("Company Name")
            with col_b:
                new_v_cat = st.selectbox("Assign Category", st.session_state.categories)
                new_v_status = st.selectbox("Initial Status", ["Active", "Under Review", "Onboarding"])
            
            st.divider()
            
            
            st.write("#### 2. KYC & Compliance (Indian Regulations)")
            col_kyc1, col_kyc2 = st.columns(2)
            with col_kyc1:
                new_v_gstin = st.text_input("GSTIN (15 Characters)", max_chars=15)
                new_v_pan = st.text_input("Company PAN (10 Characters)", max_chars=10)
            with col_kyc2:
                new_v_bank = st.text_input("Bank Account Number")
                new_v_ifsc = st.text_input("IFSC Code", max_chars=11)
            
            st.divider()
            
            st.write("#### 3. Initial Assessment (1-10)")
            st.caption("You can leave these as 5 for now and formally evaluate them later in the Grading System.")
            
            initial_grades = {}
            grade_cols = st.columns(5)
            for i in range(5):
                with grade_cols[i]:
                    initial_grades[METRICS[i]] = st.number_input(METRICS[i], min_value=1, max_value=10, value=5)
            
            submit_vendor = st.form_submit_button("Register & Save KYC")
            
            if submit_vendor:
                if not new_v_id or not new_v_name:
                    st.error("Vendor ID and Name are required!")
                elif len(new_v_gstin) > 0 and len(new_v_gstin) != 15:
                    st.warning("GSTIN must be exactly 15 characters long if provided.")
                elif len(new_v_pan) > 0 and len(new_v_pan) != 10:
                    st.warning("PAN must be exactly 10 characters long if provided.")
                else:
                    initial_score = sum(initial_grades.values()) / 5
                    initial_grade = calculate_grade(initial_score)
                    
                    new_data = {
                        'Vendor ID': new_v_id,
                        'Name': new_v_name,
                        'Category': new_v_cat,
                        'Status': new_v_status,
                        'GSTIN': new_v_gstin.upper(),
                        'PAN': new_v_pan.upper(),
                        'Bank Account': new_v_bank,
                        'IFSC Code': new_v_ifsc.upper(),
                        'Final Score (out of 10)': initial_score,
                        'Final Grade': initial_grade
                    }
                    
                    for metric in METRICS:
                        new_data[metric] = initial_grades[metric]
                        
                    st.session_state.vendors = pd.concat([st.session_state.vendors, pd.DataFrame([new_data])], ignore_index=True)
                    st.success(f"✅ {new_v_name} has been added to the directory with KYC records!")

   
    with tab2:
        st.write("### Add Custom Vendor Categories")
        st.write("Current categories available in your system:")
        
        for cat in st.session_state.categories:
            st.markdown(f"- {cat}")
            
        st.divider()
        
        with st.form("add_category_form"):
            new_category = st.text_input("Type new category name (e.g., 'Rail Freight', 'Packaging')")
            submit_cat = st.form_submit_button("Add Category")
            
            if submit_cat:
                if new_category == "":
                    st.error("Please type a name before submitting.")
                elif new_category in st.session_state.categories:
                    st.warning("This category already exists!")
                else:
                    st.session_state.categories.append(new_category)
                    st.success(f"✅ '{new_category}' has been added! It will now appear in all dropdown menus.")
                    st.rerun()


elif page == "Vendor Grading System":
    st.title("Vendor Evaluation & Scoring")
    st.write("Allocate percentage weights and input grades (1-10) to calculate the final score.")
    
    vendor_name = st.selectbox("Select Logistics Partner:", st.session_state.vendors['Name'])
    idx = st.session_state.vendors.index[st.session_state.vendors['Name'] == vendor_name][0]
    vendor_data = st.session_state.vendors.loc[idx]
    
    st.subheader(f"Current Status: {vendor_data['Final Grade']} (Score: {vendor_data['Final Score (out of 10)']:.1f} / 10)")

    with st.form("grading_form"):
        st.write("### 1. Set Metric Weights (%)")
        st.caption("Ensure your total weights add up to exactly 100%.")
        
        cols = st.columns(5)
        weights = []
        for i in range(5):
            with cols[i]:
                w = st.number_input(f"{METRICS[i]} Weight (%)", min_value=0, max_value=100, value=20, step=5)
                weights.append(w)
        
        total_weight = sum(weights)
        if total_weight != 100:
            st.warning(f"⚠️ Warning: Total weights currently equal {total_weight}%. They should equal 100%.")
        else:
            st.success("✅ Weights total 100%.")

        st.divider()

        st.write("### 2. Input Grades (Scale: 1 to 10)")
        
        grades = []
        grade_cols = st.columns(5)
        for i in range(5):
            with grade_cols[i]:
                current_grade = int(vendor_data[METRICS[i]])
                g = st.slider(f"{METRICS[i]} Grade", min_value=1, max_value=10, value=current_grade)
                grades.append(g)
            
        submit = st.form_submit_button("Calculate Final Score")
        
        if submit:
            if total_weight != 100:
                st.error("Cannot calculate! Please fix your weights to equal exactly 100%.")
            else:
                final_score = sum([grades[i] * (weights[i] / 100) for i in range(5)])
                final_grade = calculate_grade(final_score)
                
                for i in range(5):
                    st.session_state.vendors.at[idx, METRICS[i]] = grades[i]
                
                st.session_state.vendors.at[idx, 'Final Score (out of 10)'] = final_score
                st.session_state.vendors.at[idx, 'Final Grade'] = final_grade
                
                st.success(f"✅ Successfully updated {vendor_name}!")
                st.info(f"**Final Calculated Score:** {final_score:.1f} / 10 | **Assigned Grade:** {final_grade}")
