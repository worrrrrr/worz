"""
Finance Engine - WORZ SOVEREIGN CORE
รองรับ: ดอกเบี้ย, เงินผ่อน, ROI, NPV, การคำนวณทางการเงิน
Symbolic-only mode (ไม่ใช้ LLM)
"""

import math
from typing import Any, Dict, List, Optional
from .base_engine import BaseEngine

class FinanceEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="finance", version="1.0")
    
    def execute(self, params: Dict[str, Any]) -> str:
        """ประมวลผลคำสั่งทางการเงิน"""
        action = params.get("action", "").lower()
        expression = params.get("expression", "")
        
        # ตรวจสอบประเภทคำสั่ง
        if "ดอกเบี้ย" in action or "interest" in action:
            return self._calculate_interest(params)
        elif "ผ่อน" in action or "installment" in action or "loan" in action:
            return self._calculate_installment(params)
        elif "roi" in action or "ผลตอบแทน" in action or "return" in action:
            return self._calculate_roi(params)
        elif "npv" in action or "มูลค่าปัจจุบัน" in action:
            return self._calculate_npv(params)
        elif "fv" in action or "มูลค่าอนาคต" in action or "future" in action:
            return self._calculate_fv(params)
        elif "break-even" in action or "จุดคุ้มทุน" in action:
            return self._calculate_break_even(params)
        else:
            return self._auto_detect(expression, params)
    
    def _calculate_interest(self, params: Dict[str, Any]) -> str:
        """คำนวณดอกเบี้ย (Simple & Compound)"""
        principal = float(params.get("principal", params.get("amount", 0)))
        rate = float(params.get("rate", 0)) / 100  # แปลงเป็นทศนิยม
        time = float(params.get("time", params.get("years", 1)))
        compound = params.get("compound", False) or "compound" in str(params).lower()
        n_compound = int(params.get("n_compound", params.get("frequency", 1)))  # ครั้งต่อปี
        
        result = []
        result.append(f"💰 การคำนวณดอกเบี้ย:")
        result.append(f"   เงินต้น: {principal:,.2f} บาท")
        result.append(f"   อัตราดอกเบี้ย: {rate*100:.2f}% ต่อปี")
        result.append(f"   ระยะเวลา: {time} ปี")
        
        if compound:
            # ดอกเบี้ยทบต้น
            result.append(f"   ประเภท: ดอกเบี้ยทบต้น ({n_compound} ครั้ง/ปี)")
            amount = principal * (1 + rate/n_compound)**(n_compound*time)
            interest = amount - principal
            result.append(f"\n   💵 เงินรวมปลายทาง: {amount:,.2f} บาท")
            result.append(f"   💵 ดอกเบี้ยรับ: {interest:,.2f} บาท")
            result.append(f"   สูตร: A = P(1 + r/n)^(nt)")
        else:
            # ดอกเบี้ยธรรมดา
            result.append(f"   ประเภท: ดอกเบี้ยธรรมดา")
            interest = principal * rate * time
            amount = principal + interest
            result.append(f"\n   💵 เงินรวมปลายทาง: {amount:,.2f} บาท")
            result.append(f"   💵 ดอกเบี้ยรับ: {interest:,.2f} บาท")
            result.append(f"   สูตร: I = P × r × t")
        
        return "\n".join(result)
    
    def _calculate_installment(self, params: Dict[str, Any]) -> str:
        """คำนวณเงินผ่อนชำระ (Loan Amortization)"""
        loan_amount = float(params.get("loan", params.get("amount", 0)))
        annual_rate = float(params.get("rate", 0)) / 100
        years = float(params.get("years", params.get("time", 1)))
        
        if loan_amount <= 0 or annual_rate <= 0 or years <= 0:
            return "⚠️ กรุณาระบุจำนวนเงินกู้ อัตราดอกเบี้ย และระยะเวลาให้ถูกต้อง"
        
        # คำนวณค่างวดรายเดือน
        monthly_rate = annual_rate / 12
        n_payments = int(years * 12)
        
        # สูตร: PMT = P × [r(1+r)^n] / [(1+r)^n - 1]
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        else:
            monthly_payment = loan_amount / n_payments
        
        total_payment = monthly_payment * n_payments
        total_interest = total_payment - loan_amount
        
        result = []
        result.append(f"🏦 การคำนวณเงินผ่อนชำระ:")
        result.append(f"   จำนวนเงินกู้: {loan_amount:,.2f} บาท")
        result.append(f"   อัตราดอกเบี้ย: {annual_rate*100:.2f}% ต่อปี")
        result.append(f"   ระยะเวลา: {years} ปี ({n_payments} งวด)")
        result.append(f"\n   💳 ค่างวดรายเดือน: {monthly_payment:,.2f} บาท")
        result.append(f"   💳 ยอดชำระรวม: {total_payment:,.2f} บาท")
        result.append(f"   💳 ดอกเบี้ยรวม: {total_interest:,.2f} บาท")
        result.append(f"   สูตร: PMT = P × [r(1+r)^n] / [(1+r)^n - 1]")
        
        # ตาราง amortization แบบย่อ (3 งวดแรกและ 3 งวดสุดท้าย)
        if params.get("show_schedule", False):
            result.append(f"\n📋 ตารางผ่อนชำระ (ย่อ):")
            balance = loan_amount
            for i in range(1, min(4, n_payments+1)):
                interest_part = balance * monthly_rate
                principal_part = monthly_payment - interest_part
                balance -= principal_part
                result.append(f"   งวด {i}: ดอกเบี้ย {interest_part:,.2f} | ต้นเงิน {principal_part:,.2f} | คงเหลือ {balance:,.2f}")
            
            if n_payments > 6:
                result.append(f"   ...")
                # แสดง 3 งวดสุดท้าย
                balance = loan_amount
                for i in range(1, n_payments+1):
                    interest_part = balance * monthly_rate
                    principal_part = monthly_payment - interest_part
                    balance -= principal_part
                    if i >= n_payments - 2:
                        result.append(f"   งวด {i}: ดอกเบี้ย {interest_part:,.2f} | ต้นเงิน {principal_part:,.2f} | คงเหลือ {balance:,.2f}")
        
        return "\n".join(result)
    
    def _calculate_roi(self, params: Dict[str, Any]) -> str:
        """คำนวณผลตอบแทนการลงทุน (Return on Investment)"""
        initial = float(params.get("initial", params.get("cost", params.get("investment", 0))))
        final = float(params.get("final", params.get("value", params.get("return", 0))))
        period = float(params.get("period", params.get("years", 1)))
        
        if initial <= 0:
            return "⚠️ เงินลงทุนเริ่มต้นต้องมากกว่า 0"
        
        gain = final - initial
        roi = (gain / initial) * 100
        annualized_roi = ((final / initial)**(1/period) - 1) * 100 if period > 0 else 0
        
        result = []
        result.append(f"📈 การคำนวณ ROI:")
        result.append(f"   เงินลงทุน: {initial:,.2f} บาท")
        result.append(f"   มูลค่าปัจจุบัน: {final:,.2f} บาท")
        result.append(f"   ระยะเวลา: {period} ปี")
        result.append(f"\n   💰 กำไร/ขาดทุน: {gain:,.2f} บาท")
        result.append(f"   📊 ROI: {roi:.2f}%")
        result.append(f"   📊 Annualized ROI: {annualized_roi:.2f}% ต่อปี")
        result.append(f"   สูตร: ROI = (Gain - Cost) / Cost × 100")
        
        # ให้คำแนะนำ
        if roi > 0:
            result.append(f"\n   ✅ การลงทุนมีกำไร")
        else:
            result.append(f"\n   ⚠️ การลงทุนขาดทุน")
        
        return "\n".join(result)
    
    def _calculate_npv(self, params: Dict[str, Any]) -> str:
        """คำนวณมูลค่าปัจจุบันสุทธิ (Net Present Value)"""
        initial_investment = float(params.get("initial", params.get("cost", 0)))
        cash_flows = params.get("cash_flows", [])
        discount_rate = float(params.get("rate", params.get("discount", 0))) / 100
        
        if isinstance(cash_flows, str):
            # Parse จาก string เช่น "100,200,300,400"
            try:
                cash_flows = [float(x.strip()) for x in cash_flows.split(",")]
            except:
                return "⚠️ รูปแบบ cash flows ไม่ถูกต้อง ใช้รูปแบบ '100,200,300,...'"
        
        if not cash_flows:
            return "⚠️ กรุณาระบุกระแสเงินสด (cash_flows)"
        
        # คำนวณ NPV
        npv = -initial_investment
        details = []
        for t, cf in enumerate(cash_flows, 1):
            pv = cf / ((1 + discount_rate)**t)
            npv += pv
            details.append(f"   ปี {t}: {cf:,.2f} → PV = {pv:,.2f}")
        
        result = []
        result.append(f"💼 การคำนวณ NPV:")
        result.append(f"   เงินลงทุนเริ่มต้น: {initial_investment:,.2f} บาท")
        result.append(f"   อัตราคิดลด: {discount_rate*100:.2f}%")
        result.append(f"   กระแสเงินสด: {cash_flows}")
        result.append(f"\n   รายละเอียด PV แต่ละปี:")
        result.extend(details)
        result.append(f"\n   💵 NPV = {npv:,.2f} บาท")
        result.append(f"   สูตร: NPV = Σ [CF_t / (1+r)^t] - Initial Investment")
        
        if npv > 0:
            result.append(f"\n   ✅ โครงการน่าลงทุน (NPV > 0)")
        elif npv < 0:
            result.append(f"\n   ⚠️ โครงการไม่น่าลงทุน (NPV < 0)")
        else:
            result.append(f"\n   ⚖️ จุดคุ้มทุน (NPV = 0)")
        
        return "\n".join(result)
    
    def _calculate_fv(self, params: Dict[str, Any]) -> str:
        """คำนวณมูลค่าในอนาคต (Future Value)"""
        pv = float(params.get("pv", params.get("present", params.get("amount", 0))))
        rate = float(params.get("rate", 0)) / 100
        periods = int(params.get("periods", params.get("years", 1)))
        pmt = float(params.get("pmt", params.get("payment", 0)))  # เงินฝากเพิ่มรายงวด
        
        if pmt > 0:
            # มีเงินฝากเพิ่มแต่ละงวด
            fv_lumpsum = pv * (1 + rate)**periods
            fv_annuity = pmt * (((1 + rate)**periods - 1) / rate) if rate > 0 else pmt * periods
            fv = fv_lumpsum + fv_annuity
            result = []
            result.append(f"🔮 การคำนวณมูลค่าในอนาคต (มีเงินฝากเพิ่ม):")
            result.append(f"   เงินเริ่มต้น: {pv:,.2f} บาท")
            result.append(f"   เงินฝากเพิ่มงวดละ: {pmt:,.2f} บาท")
            result.append(f"   อัตราดอกเบี้ย: {rate*100:.2f}%")
            result.append(f"   ระยะเวลา: {periods} งวด")
            result.append(f"\n   FV จากเงินก้อน: {fv_lumpsum:,.2f} บาท")
            result.append(f"   FV จากเงินฝากเพิ่ม: {fv_annuity:,.2f} บาท")
            result.append(f"   💵 FV รวม: {fv:,.2f} บาท")
        else:
            # ไม่มีเงินฝากเพิ่ม
            fv = pv * (1 + rate)**periods
            result = []
            result.append(f"🔮 การคำนวณมูลค่าในอนาคต:")
            result.append(f"   เงินเริ่มต้น: {pv:,.2f} บาท")
            result.append(f"   อัตราดอกเบี้ย: {rate*100:.2f}%")
            result.append(f"   ระยะเวลา: {periods} ปี")
            result.append(f"\n   💵 FV = {fv:,.2f} บาท")
            result.append(f"   สูตร: FV = PV × (1 + r)^n")
        
        return "\n".join(result)
    
    def _calculate_break_even(self, params: Dict[str, Any]) -> str:
        """คำนวณจุดคุ้มทุน (Break-Even Point)"""
        fixed_cost = float(params.get("fixed", params.get("fc", 0)))
        price = float(params.get("price", 0))
        variable_cost = float(params.get("variable", params.get("vc", params.get("unit_cost", 0))))
        
        if price <= variable_cost:
            return "⚠️ ราคาขายต้องสูงกว่าต้นทุนผันแปรต่อหน่วย"
        
        contribution_margin = price - variable_cost
        break_even_units = fixed_cost / contribution_margin
        break_even_revenue = break_even_units * price
        
        result = []
        result.append(f"⚖️ การคำนวณจุดคุ้มทุน:")
        result.append(f"   ต้นทุนคงที่: {fixed_cost:,.2f} บาท")
        result.append(f"   ราคาขายต่อหน่วย: {price:,.2f} บาท")
        result.append(f"   ต้นทุนผันแปรต่อหน่วย: {variable_cost:,.2f} บาท")
        result.append(f"\n   📊 Contribution Margin: {contribution_margin:,.2f} บาท/หน่วย")
        result.append(f"   📊 จุดคุ้มทุน (หน่วย): {break_even_units:.2f} หน่วย")
        result.append(f"   📊 จุดคุ้มทุน (บาท): {break_even_revenue:,.2f} บาท")
        result.append(f"   สูตร: BEP(units) = FC / (Price - VC)")
        
        return "\n".join(result)
    
    def _auto_detect(self, expression: str, params: Dict[str, Any]) -> str:
        """พยายามตรวจจับประเภทคำสั่งอัตโนมัติ"""
        expression_lower = expression.lower()
        
        # ตรวจสอบ keywords
        if any(kw in expression_lower for kw in ['ดอกเบี้ย', 'interest', 'ฝาก', 'ธนาคาร']):
            return self._calculate_interest(params)
        elif any(kw in expression_lower for kw in ['ผ่อน', 'รถ', 'บ้าน', 'loan', 'installment']):
            return self._calculate_installment(params)
        elif any(kw in expression_lower for kw in ['roi', 'หุ้น', 'ลงทุน', 'return', 'profit']):
            return self._calculate_roi(params)
        elif any(kw in expression_lower for kw in ['npv', 'โครงการ', 'invest']):
            return self._calculate_npv(params)
        elif any(kw in expression_lower for kw in ['จุดคุ้มทุน', 'break-even', 'bec']):
            return self._calculate_break_even(params)
        
        # Default
        return "💼 Finance Engine พร้อมใช้งาน\nคำสั่งที่รองรับ:\n- ดอกเบี้ย: 'ดอกเบี้ย 10000 บาท ที่ 5% 3 ปี'\n- เงินผ่อน: 'ผ่อนรถ 500000 บาท ดอก 7% 5 ปี'\n- ROI: 'ROI ลงทุน 100000 ได้กลับมา 150000'\n- NPV: 'NPV ลงทุน 100000 cash flows 30000,40000,50000 rate 10%'\n- จุดคุ้มทุน: 'จุดคุ้มทุน fixed 50000 price 100 vc 60'"
