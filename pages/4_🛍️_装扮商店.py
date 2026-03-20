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
st.caption(f"当前积分: {balance}")

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
    cols = st.columns(min(4, len(items)))
    for i, item in enumerate(items):
        with cols[i % len(cols)]:
            is_owned = item["id"] in owned
            is_equipped = pet.get("equipped", {}).get(cat) == item["id"]

            st.markdown(f"""
            <div style="text-align:center; padding:0.5rem; border:1px solid #ddd; border-radius:8px; margin-bottom:0.5rem;">
            <div style="font-size:2.5rem;">{item['emoji']}</div>
            <div><b>{item['name']}</b></div>
            <div>{'✅ 已拥有' if is_owned else f"💰 {item['price']}积分"}</div>
            </div>
            """, unsafe_allow_html=True)

            if is_equipped:
                st.success("已装备", icon="✅")
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
                        st.success(f"购买成功！{msg}")
                        st.rerun()
                    else:
                        st.error(msg)
    st.divider()
