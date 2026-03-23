"""装扮商店页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.points_engine import get_balance, spend_points
from utils.pet_engine import get_pet, equip_item
from utils.data_io import read_json, update_dict
from config import SHOP_ITEMS, CATEGORY_NAMES

st.set_page_config(page_title="装扮商店", page_icon="🛍️")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
balance = get_balance(sid)
pet = get_pet(sid)

st.title("🛍️ 装扮商店")
st.metric("当前积分", balance)

# 读取用户已购物品
shop_data = read_json("shop.json")
if not isinstance(shop_data, dict):
    shop_data = {}
owned = shop_data.get(sid, [])

# 按分类展示
categories = {}
for item in SHOP_ITEMS:
    cat = item["category"]
    categories.setdefault(cat, []).append(item)

for cat, items in categories.items():
    st.subheader(f"{CATEGORY_NAMES.get(cat, cat)}")
    # 手机端 2 列，桌面端最多 4 列
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            is_owned = item["id"] in owned
            is_equipped = pet.get("equipped", {}).get(cat) == item["id"]

            # 状态标签
            if is_equipped:
                badge = "✅ 已装备"
                badge_color = "#4CAF50"
            elif is_owned:
                badge = "已拥有"
                badge_color = "#2196F3"
            else:
                badge = f"💰 {item['price']}分"
                badge_color = "#FF9800"

            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem 0.5rem; border:2px solid {'#4CAF50' if is_equipped else '#e0e0e0'};
                border-radius:14px; margin-bottom:0.5rem; background:{'#f0fff0' if is_equipped else 'white'};">
                <div style="font-size:2.2rem;">{item['emoji']}</div>
                <div style="font-weight:600; font-size:0.95rem; margin:0.2rem 0;">{item['name']}</div>
                <div style="color:{badge_color}; font-size:0.85rem; font-weight:500;">{badge}</div>
            </div>
            """, unsafe_allow_html=True)

            if is_equipped:
                if st.button("卸下", key=f"unequip_{item['id']}", use_container_width=True):
                    equip_item(sid, cat, None)
                    st.rerun()
            elif is_owned:
                if st.button("装备", key=f"equip_{item['id']}", use_container_width=True):
                    equip_item(sid, cat, item["id"])
                    st.rerun()
            else:
                if st.button(f"购买", key=f"buy_{item['id']}", use_container_width=True):
                    ok, msg = spend_points(sid, item["price"], f"购买 {item['name']}")
                    if ok:
                        owned.append(item["id"])
                        shop_data[sid] = owned
                        update_dict("shop.json", sid, owned)
                        st.toast(f"购买成功！{msg}")
                        st.rerun()
                    else:
                        st.error(msg)
    st.divider()
