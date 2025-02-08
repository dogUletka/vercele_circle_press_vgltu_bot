export default async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ success: false, message: 'Метод не разрешен' });
    }

    try {
        const file = req.files?.video;
        if (!file) {
            return res.status(400).json({ success: false, message: 'Видео не найдено' });
        }

        // Проверка размера файла (максимум 500 МБ)
        if (file.size > 100 * 1024 * 1024) {
            return res.status(400).json({ success: false, message: 'Файл слишком большой. Максимальный размер — 100 МБ.' });
        }

        // Проверка типа файла
        if (!file.mimetype.startsWith('video/')) {
            return res.status(400).json({ success: false, message: 'Пожалуйста, загрузите видеофайл.' });
        }

        // Сохраняем видео (в реальном проекте используйте облачное хранилище)
        const fileUrl = `/uploads/${file.name}`;
        await file.mv(`./public${fileUrl}`);

        res.status(200).json({ success: true, file_url: fileUrl });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Ошибка сервера при загрузке видео.' });
    }
};