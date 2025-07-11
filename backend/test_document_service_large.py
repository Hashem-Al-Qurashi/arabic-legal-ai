import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.storage.sqlite_store import SqliteVectorStore
from app.services.document_service import DocumentService

async def test_large_document():
    """Test DocumentService with actual large legal document"""
    load_dotenv()
    
    try:
        storage = SqliteVectorStore("data/vectors.db")
        await storage.initialize()
        
        ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        doc_service = DocumentService(storage, ai_client)
        
        # Real large Saudi legal document content (excerpt)
        large_legal_content = """
        اللوائح التنفيذية لنظام المرافعات الشرعية

        الباب الأول: التعريفات والأحكام العامة

        المادة الأولى: يُقصد بالمصطلحات الواردة في هذه اللائحة المعاني المبينة أمام كل منها:
        1. النظام: نظام المرافعات الشرعية الصادر بالمرسوم الملكي رقم (م/1) وتاريخ 22/1/1435هـ.
        2. اللائحة: اللائحة التنفيذية لنظام المرافعات الشرعية.
        3. المحكمة: أي محكمة من محاكم المملكة العربية السعودية.
        4. المتقاضي: كل من المدعي والمدعى عليه وسائر الخصوم.
        5. الدعوى: الطلب المتضمن إلزام الخصم بأداء شيء أو الامتناع عنه.

        المادة الثانية: تطبق أحكام هذه اللائحة على جميع الدعاوى والإجراءات المنصوص عليها في النظام.

        المادة الثالثة: يجب على كل من يتولى القضاء أو يعمل في الجهاز القضائي التقيد بأحكام النظام وهذه اللائحة.

        الباب الثاني: صحيفة الدعوى وإجراءات تقديمها

        المادة الرابعة: يجب على المدعي تقديم صحيفة الدعوى مشتملة على البيانات التالية:
        1. اسم المحكمة المرفوعة إليها الدعوى.
        2. اسم المدعي ولقبه ومهنته ومحل إقامته.
        3. اسم المدعى عليه ولقبه ومهنته ومحل إقامته.
        4. تاريخ تقديم صحيفة الدعوى.
        5. وقائع الدعوى وأسانيدها.
        6. طلبات المدعي.
        7. توقيع المدعي أو وكيله.

        المادة الخامسة: إذا تعدد المدعي عليهم وجب ذكر اسم كل منهم ولقبه ومهنته ومحل إقامته.

        المادة السادسة: يجوز للمدعي أن يودع مع صحيفة الدعوى المستندات المؤيدة لدعواه.

        الباب الثالث: إجراءات التبليغ والإعلان

        المادة السابعة: يكون التبليغ بتسليم صورة من الصحيفة أو الورقة المراد تبليغها إلى المراد تبليغه شخصياً.

        المادة الثامنة: إذا لم يوجد المراد تبليغه في محل إقامته فيسلم التبليغ إلى من يوجد من أهل بيته البالغين.

        المادة التاسعة: إذا امتنع المراد تبليغه أو من ينوب عنه عن تسلم التبليغ فيترك التبليغ في محل إقامته.

        الباب الرابع: الجلسات والمرافعات

        المادة العاشرة: تكون الجلسات علنية إلا إذا رأت المحكمة من تلقاء نفسها أو بناءً على طلب أحد الخصوم جعلها سرية.

        المادة الحادية عشرة: للمحكمة أن تسمع الدعوى في غياب أحد الخصوم إذا كان التبليغ صحيحاً.

        المادة الثانية عشرة: يجوز للخصم أن يترافع بنفسه أو بواسطة وكيل معتمد من المحكمة.

        الباب الخامس: الأحكام وتنفيذها

        المادة الثالثة عشرة: تصدر الأحكام باسم الملك وتشتمل على الأسباب التي بنيت عليها.

        المادة الرابعة عشرة: يجب أن يكون الحكم واضحاً قابلاً للتنفيذ.

        المادة الخامسة عشرة: تنفذ الأحكام النهائية بعد انقضاء مدة الاعتراض أو بعد الفصل في الاعتراض.

        الباب السادس: الطعن في الأحكام

        المادة السادسة عشرة: يجوز الطعن في الأحكام وفقاً للأحكام المنصوص عليها في النظام.

        المادة السابعة عشرة: يجب تقديم الطعن خلال المدة المحددة في النظام.

        المادة الثامنة عشرة: يترتب على تقديم الطعن وقف تنفيذ الحكم إلا في الحالات المستثناة.
        """ * 15  # Multiply to make it realistically large (around 15K+ tokens)
        
        large_doc = [{
            "title": "اللوائح التنفيذية لنظام المرافعات الشرعية",
            "content": large_legal_content,
            "metadata": {
                "source": "ministry_of_justice",
                "document_type": "executive_regulations",
                "legal_system": "sharia_procedures"
            }
        }]
        
        print(f"📄 Document: {large_doc[0]['title']}")
        print(f"📏 Content length: {len(large_doc[0]['content']):,} chars")
        print(f"🔢 Estimated tokens: {len(large_doc[0]['content']) // 2:,}")
        print()
        
        print("🧪 Testing Large Document Processing...")
        result = await doc_service.add_documents_batch(large_doc)
        print(f"✅ Result: {result}")
        
        # Check what was stored
        print("\n📊 Storage Status:")
        health = await doc_service.get_storage_health()
        print(f"🏥 Storage Health: {health}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_large_document())
