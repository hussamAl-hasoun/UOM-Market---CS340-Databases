project/
├── app.py              # تشغيل المشروع + المسارات
├── db.py               # الاتصال بالقاعدة
├── database/
│   ├── schema.sql      # الجداول والقيود
│   └── seed.sql        # بيانات تجريبية
├── templates/          # صفحات HTML
├── static/             # CSS
└── README.md



شرح القيود (بسيط)
القيد	وش يسوي	مثال
PRIMARY KEY	رقم فريد لكل صف، ما يكون NULL	user_id
UNIQUE على الإيميل	ما يتكرر إيميل	ما يسجل اثنين بنفس الإيميل
CHECK (price >= 0)	السعر ما يكون سالب	سعر -5 يترفض
ON DELETE CASCADE	تنحذف الصفوف المرتبطة معه	احذف بائع، تنحذف إعلاناته
ON DELETE SET NULL	يصير الربط NULL والصف يبقى	احذف تصنيف، الإعلان يبقى بدون تصنيف
ON DELETE RESTRICT	يمنع الحذف	إعلان عليه طلبات ما ينحذف