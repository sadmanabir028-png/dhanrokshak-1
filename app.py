import streamlit as st
import numpy as np
from PIL import Image
import time
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ধানরক্ষক - AI রোগ শনাক্তকরণ",
    page_icon="https://www.pinterest.com/pin/76209418689740748/",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bengali interface
st.markdown("""
<style>
    .main {
        direction: ltr;
    }
    .bengali-font {
        font-family: 'Noto Sans Bengali', 'SolaimanLipi', 'Kalpurush', sans-serif;
    }
    .success-box {
        background: linear-gradient(135deg, #E8F5E8, #FFFFFF);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #2E8B57;
        margin: 10px 0;
    }
    .disease-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #E0E0E0;
    }
    .header-bg {
        background: linear-gradient(135deg, #2E8B57, #1A5D1A);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .upload-box {
        border: 2px dashed #2E8B57;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        background: #F8FFF8;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

class RiceDiseaseDetector:
    def __init__(self):
        self.disease_info = {
            'Healthy': {
                'bn_name': 'সুস্থ ধান',
                'type': 'সুস্থ',
                'symptoms': 'সবুজ ও স্বাস্থ্যকর পাতা, কোনো দাগ বা ক্ষত নেই',
                'treatment': [
                    'নিয়মিত পর্যবেক্ষণ চালিয়ে যান',
                    'সুষম সার ব্যবহার করুন',
                    'পর্যাপ্ত সেচ ও সূর্যালোক নিশ্চিত করুন'
                ],
                'prevention': [
                    'সঠিক দূরত্বে চারা রোপণ করুন',
                    'সময়মতো সেচ ও সার প্রয়োগ করুন',
                    'জমিতে বায়ু চলাচল নিশ্চিত করুন'
                ],
                'urgency': 'কম',
                'emoji': '✅'
            },
            'Leaf_Blast': {
                'bn_name': 'ব্লাস্ট রোগ',
                'type': 'ছত্রাকজনিত',
                'symptoms': 'পাতায় ডিম্বাকৃতি বা রম্বস আকৃতির দাগ, কেন্দ্র ধূসর, প্রান্ত বাদামি',
                'treatment': [
                    'আক্রান্ত পাতাগুলো কেটে ফেলুন',
                    'ট্রাইসাইক্লাজল বা কার্বেন্ডাজিম গ্রুপের ছত্রাকনাশক ব্যবহার করুন',
                    'জমিতে পানি নিষ্কাশন নিশ্চিত করুন',
                    'স্থানীয় কৃষি অফিসারের সঙ্গে যোগাযোগ করুন'
                ],
                'prevention': [
                    'ব্লাস্ট-প্রতিরোধী জাত ব্যবহার করুন',
                    'জমিতে অতিরিক্ত নাইট্রোজেন সারের ব্যবহার এড়িয়ে চলুন',
                    'ফসল আবর্তন করুন',
                    'বীজ শোধন করুন'
                ],
                'urgency': 'উচ্চ',
                'emoji': '🦠'
            },
            'Brown_Spot': {
                'bn_name': 'বাদামি দাগ রোগ',
                'type': 'ছত্রাকজনিত',
                'symptoms': 'পাতায় গোলাকার বাদামি দাগ, প্রান্ত হলুদ',
                'treatment': [
                    'আক্রান্ত গাছ সরিয়ে ফেলুন',
                    'ম্যানকোজেব বা কার্বেন্ডাজিম গ্রুপের ছত্রাকনাশক ব্যবহার করুন',
                    'জমিতে জৈবসার যোগ করুন',
                    'সুষম সার ব্যবহার করুন'
                ],
                'prevention': [
                    'স্বাস্থ্যকর বীজ ব্যবহার করুন',
                    'বীজ শোধন করুন',
                    'জমিতে পর্যাপ্ত পটাশ সার প্রয়োগ করুন',
                    'ফসলের অবশিষ্টাংশ পুড়িয়ে ফেলুন'
                ],
                'urgency': 'মধ্যম',
                'emoji': '🔴'
            },
            'Bacterial_Blight': {
                'bn_name': 'ব্যাকটেরিয়াল ব্লাইট',
                'type': 'ব্যাকটেরিয়াজনিত',
                'symptoms': 'পাতায় পানিভেজানো দাগ যা পরে সাদা বা ধূসর হয়ে যায়',
                'treatment': [
                    'আক্রান্ত গাছ সরিয়ে ফেলুন',
                    'ব্যাকটেরিসাইড যেমন স্ট্রেপটোমাইসিন ব্যবহার করুন',
                    'জমিতে অতিরিক্ত নাইট্রোজেন সারের ব্যবহার এড়িয়ে চলুন',
                    'স্থানীয় কৃষি সম্প্রসারণ অফিসের পরামর্শ নিন'
                ],
                'prevention': [
                    'বন্যাপ্রবণ এলাকায় উঁচু বীজতলা তৈরি করুন',
                    'সেচের পানি যাতে এক জমি থেকে অন্য জমিতে না যায় সেদিকে খেয়াল রাখুন',
                    'রোগমুক্ত বীজ ব্যবহার করুন',
                    'ক্ষতিকর পোকা দমন করুন'
                ],
                'urgency': 'উচ্চ',
                'emoji': '🦠'
            }
        }
    
    def predict(self, image):
        """Simulate AI prediction with realistic confidence scores"""
        # Simulate processing time
        time.sleep(2)
        
        # Convert image to numpy array for analysis
        img_array = np.array(image)
        
        # Simple color-based analysis (in real app, use your trained model)
        avg_color = np.mean(img_array, axis=(0,1))
        
        # Realistic disease probabilities based on image characteristics
        if avg_color[1] > 150:  # High green value - likely healthy
            diseases = ['Healthy', 'Brown_Spot', 'Bacterial_Blight', 'Leaf_Blast']
            probs = [0.75, 0.15, 0.06, 0.04]
        else:  # Lower green value - likely diseased
            diseases = ['Leaf_Blast', 'Brown_Spot', 'Bacterial_Blight', 'Healthy']
            probs = [0.65, 0.20, 0.10, 0.05]
        
        # Add some randomness for realism
        probs = np.array(probs) + np.random.uniform(-0.1, 0.1, len(probs))
        probs = np.clip(probs, 0, 1)
        probs = probs / np.sum(probs)  # Normalize
        
        diagnosis = diseases[np.argmax(probs)]
        confidence = np.max(probs)
        
        confidence_scores = {diseases[i]: float(probs[i]) for i in range(len(diseases))}
        
        return diagnosis, confidence, confidence_scores

def main():
    # Header Section
    st.markdown("""
    <div class="header-bg">
        <h1 class="bengali-font">🌾 ধানরক্ষক</h1>
        <h3 class="bengali-font">কৃত্রিম বুদ্ধিমত্তা চালিত ধান রোগ শনাক্তকরণ 시스템</h3>
        <p class="bengali-font">আপনার ধান পাতার ছবি আপলোড করুন এবং তাৎক্ষণিক রোগ শনাক্তকরণ পান</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📸 ছবি আপলোড ও বিশ্লেষণ")
        
        # Image upload section with better UI
        st.markdown("""
        <div class="upload-box">
            <h3 class="bengali-font">ছবি আপলোড করুন</h3>
            <p class="bengali-font">ধান পাতার স্পষ্ট ছবি নির্বাচন করুন</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "ফাইল নির্বাচন করুন",
            type=['jpg', 'jpeg', 'png'],
            help="স্পষ্ট এবং ভালো আলোযুক্ত ছবি আপলোড করুন",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="আপনার আপলোড করা ছবি", use_column_width=True)
            
            # Analysis button
            if st.button("🤖 AI বিশ্লেষণ শুরু করুন", type="primary", use_container_width=True):
                with st.spinner('আপনার ছবি বিশ্লেষণ করা হচ্ছে... কয়েক সেকেন্ড সময় নিতে পারে'):
                    detector = RiceDiseaseDetector()
                    diagnosis, confidence, confidence_scores = detector.predict(image)
                    
                    disease_info = detector.disease_info.get(diagnosis, {})
                    
                    # Display results
                    st.markdown(f"""
                    <div class="success-box">
                        <h3 class="bengali-font">🎯 রোগ শনাক্তকরণ ফলাফল</h3>
                        <p class="bengali-font"><strong>রোগ:</strong> {disease_info.get('emoji', '')} {disease_info.get('bn_name', diagnosis)}</p>
                        <p class="bengali-font"><strong>আত্মবিশ্বাস:</strong> {confidence*100:.1f}%</p>
                        <p class="bengali-font"><strong>রোগের ধরন:</strong> {disease_info.get('type', 'অজানা')}</p>
                        <p class="bengali-font"><strong>জরুরীত্ব:</strong> {disease_info.get('urgency', 'মধ্যম')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Symptoms
                    st.subheader("🔍 লক্ষণসমূহ")
                    st.info(disease_info.get('symptoms', 'লক্ষণের তথ্য পাওয়া যায়নি'))
                    
                    # Treatment advice
                    st.subheader("💊 চিকিৎসা পরামর্শ")
                    for i, treatment in enumerate(disease_info.get('treatment', []), 1):
                        st.write(f"{i}. {treatment}")
                    
                    # Prevention advice
                    st.subheader("🛡️ প্রতিরোধ ব্যবস্থা")
                    for i, prevention in enumerate(disease_info.get('prevention', []), 1):
                        st.write(f"{i}. {prevention}")
                    
                    # Confidence scores chart
                    st.subheader("📊 সমস্ত রোগের সম্ভাবনা")
                    conf_df = pd.DataFrame({
                        'রোগ': [detector.disease_info.get(d, {}).get('bn_name', d) for d in confidence_scores.keys()],
                        'সম্ভাবনা (%)': [score * 100 for score in confidence_scores.values()]
                    }).sort_values('সম্ভাবনা (%)', ascending=False)
                    
                    st.bar_chart(conf_df.set_index('রোগ'))
    
    with col2:
        st.header("ℹ️ ব্যবহার নির্দেশিকা")
        
        st.markdown("""
        <div class="disease-card">
        <h4 class="bengali-font">কীভাবে ব্যবহার করবেন:</h4>
        <ol class="bengali-font">
        <li><strong>ছবি তুলুন:</strong> ধান পাতার স্পষ্ট ছবি</li>
        <li><strong>আপলোড করুন:</strong> বাম পাশ থেকে ছবি আপলোড</li>
        <li><strong>বিশ্লেষণ করুন:</strong> AI বিশ্লেষণ বাটনে ক্লিক</li>
        <li><strong>পরামর্শ পান:</strong> রোগ শনাক্তকরণ ও চিকিৎসা</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("📋 রোগের তালিকা")
        
        detector = RiceDiseaseDetector()
        for disease, info in detector.disease_info.items():
            with st.expander(f"{info.get('emoji', '🌱')} {info['bn_name']}"):
                st.write(f"**ধরন:** {info['type']}")
                st.write(f"**জরুরীত্ব:** {info['urgency']}")
                st.write(f"**লক্ষণ:** {info['symptoms'][:100]}...")
        
        st.header("📞 জরুরি যোগাযোগ")
        st.markdown("""
        <div class="disease-card">
        <p class="bengali-font">যদি রোগ গুরুতর হয়:</p>
        <ul class="bengali-font">
        <li>স্থানীয় কৃষি অফিস</li>
        <li>কৃষি সম্প্রসারণ কর্মকর্তা</li>
        <li>ধান গবেষণা ইনস্টিটিউট</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("💡 ছবি তোলার টিপস")
        st.markdown("""
        <div class="disease-card">
        <ul class="bengali-font">
        <li>প্রাকৃতিক আলোতে ছবি তুলুন</li>
        <li>ক্লোজ-আপ শট নিন</li>
        <li>পাতার ক্ষত স্পষ্ট দেখান</li>
        <li>ঝাপসা ছবি এড়িয়ে চলুন</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p class="bengali-font">© ২০২৪ ধানরক্ষক - কৃষকের জন্য AI সমাধান</p>
        <p class="bengali-font">বাংলাদেশ ও ভারতের কৃষকদের জন্য নিবেদিত</p>
        <p><small>Made with ❤️ for Farmers</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
