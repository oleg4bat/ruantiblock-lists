# Ruantiblock lists

Списки для выборочной маршрутизации трафика через Ruantiblock. Разбиты на категории, автоматически публикуются одним файлом.

**Одна ссылка для подключения:**

```text
https://raw.githubusercontent.com/oleg4bat/ruantiblock-lists/main/all.txt
```

## Структура

- `lists/domains/`: домены по сервисам (Google AI, OpenAI, Anthropic, YouTube, Discord, Telegram и другое).
- `lists/ips/`: Discord и Telegram. Широкие IP-подсети Discord намеренно сохранены после тестирования голосовой связи.
- `config/approved-broad-cidrs.txt`: разрешённые широкие IP-подсети.
- `scripts/build.py`: сборка `all.txt`, `domains.txt`, `ips.txt` из категорий с удалением дублирующихся поддоменов и схлопыванием пересекающихся IP-сетей.
- `.github/workflows/build.yml`: GitHub Actions для автоматической публикации.

## Редактирование

Меняйте файлы в `lists/` и отправляйте изменения в `main`. GitHub Actions обновит `all.txt` без изменения его URL.

**Не удалять широкие подсети Discord только из-за размера:** они были экспериментально подобраны для работы Discord Voice; общие диапазоны Cloudflare и Google Cloud могут при этом затрагивать посторонний трафик.

Для локальной сборки: `python3 scripts/build.py`.
