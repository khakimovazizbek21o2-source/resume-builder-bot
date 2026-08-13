@router.callback_query(F.data == "generate_pdf")
async def cb_generate_pdf(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await call.message.answer("Ma'lumotlar topilmadi. Qaytadan /start bosing.")
        await call.answer()
        return

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("⏳ PDF rezyumengiz tayyorlanmoqda...")
    
    pdf_path = f"resume_{call.from_user.id}.pdf"

    try:
        # 1. PDF yaratish
        create_resume_pdf(data, pdf_path)

        # 2. Faqat PDF faylni yuborish
        doc = FSInputFile(pdf_path)
        await call.message.answer_document(
            document=doc,
            caption="🎉 <b>Sizning tayyor PDF rezyumengiz!</b>\n\nYangi rezyume yaratish uchun /start bosing.",
            parse_mode="HTML"
        )
        
        # Yuklangan profil rasmini tozalash
        photo_p = data.get("photo_path")
        if photo_p and os.path.exists(photo_p):
            os.remove(photo_p)
            
        await state.clear()

    except Exception as e:
        await call.message.answer(f"❌ PDF yaratishda xatolik yuz berdi: {str(e)}")

    finally:
        # Vaqtinchalik yaratilgan PDF faylni o'chirish
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    await call.answer()