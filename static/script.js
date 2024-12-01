// グローバル変数
let currentEditId = null;

// ページ読み込み時にエントリーを取得
document.addEventListener('DOMContentLoaded', () => {
    loadEntries();
});

// ログアウト処理
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            window.location.href = '/login';
        } else {
            alert('ログアウトに失敗しました');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

// 活動項目の収集
function collectItems() {
    const items = [];
    document.querySelectorAll('.item-entry').forEach(itemEntry => {
        const name = itemEntry.querySelector('.item-name').value.trim();
        const content = itemEntry.querySelector('.item-content').value.trim();
        if (name && content) {
            items.push({ item_name: name, item_content: content });
        }
    });
    return items;
}

// 日記エントリーを投稿
async function postEntry() {
    const title = document.getElementById('diaryTitle').value.trim();
    const content = document.getElementById('diaryContent').value.trim();
    const notes = document.getElementById('diaryNotes').value.trim();
    const items = collectItems();
    
    if (!title) {
        alert('タイトルを入力してください');
        return;
    }
    if (!content) {
        alert('内容を入力してください');
        return;
    }

    try {
        const response = await fetch('/entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content, notes, items })
        });

        if (response.ok) {
            document.getElementById('diaryTitle').value = '';
            document.getElementById('diaryContent').value = '';
            document.getElementById('diaryNotes').value = '';
            document.getElementById('itemsList').innerHTML = '';
            loadEntries();
        } else {
            const data = await response.json();
            alert(data.error || '投稿に失敗しました');
            if (response.status === 401) {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

// 活動項目の設定
function setItems(items = []) {
    const itemsList = document.getElementById('itemsList');
    itemsList.innerHTML = '';
    items.forEach(item => {
        const template = document.querySelector('.item-template').cloneNode(true);
        template.style.display = 'block';
        template.classList.remove('item-template');
        template.querySelector('.item-name').value = item.item_name;
        template.querySelector('.item-content').value = item.item_content;
        itemsList.appendChild(template);
    });
}

// 編集モードを開始
function startEdit(id, title, content, notes, items) {
    currentEditId = id;
    const titleInput = document.getElementById('diaryTitle');
    const contentTextarea = document.getElementById('diaryContent');
    const notesTextarea = document.getElementById('diaryNotes');
    titleInput.value = title;
    contentTextarea.value = content;
    notesTextarea.value = notes || '';
    setItems(items || []);
    
    // ボタンの表示を切り替え
    document.getElementById('submitButton').style.display = 'none';
    document.getElementById('updateButton').style.display = 'inline';
    document.getElementById('cancelButton').style.display = 'inline';
    
    // タイトル入力にフォーカス
    titleInput.focus();
}

// 編集をキャンセル
function cancelEdit() {
    currentEditId = null;
    document.getElementById('diaryTitle').value = '';
    document.getElementById('diaryContent').value = '';
    document.getElementById('diaryNotes').value = '';
    document.getElementById('itemsList').innerHTML = '';
    
    // ボタンの表示を元に戻す
    document.getElementById('submitButton').style.display = 'inline';
    document.getElementById('updateButton').style.display = 'none';
    document.getElementById('cancelButton').style.display = 'none';
}

// エントリーを更新
async function updateEntry() {
    if (!currentEditId) return;
    
    const title = document.getElementById('diaryTitle').value.trim();
    const content = document.getElementById('diaryContent').value.trim();
    const notes = document.getElementById('diaryNotes').value.trim();
    const items = collectItems();
    
    if (!title) {
        alert('タイトルを入力してください');
        return;
    }
    if (!content) {
        alert('内容を入力してください');
        return;
    }

    try {
        const response = await fetch(`/entries/${currentEditId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content, notes, items })
        });

        if (response.ok) {
            cancelEdit();
            loadEntries();
        } else {
            const data = await response.json();
            alert(data.error || '更新に失敗しました');
            if (response.status === 401) {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

// 日記エントリーを読み込み
async function loadEntries() {
    try {
        const response = await fetch('/entries');
        const entries = await response.json();
        
        const entriesDiv = document.getElementById('entries');
        entriesDiv.innerHTML = '';

        entries.forEach(entry => {
            const entryElement = document.createElement('div');
            entryElement.className = 'entry';
            
            // 日時の表示を整形
            const createdAt = new Date(entry.created_at).toLocaleString('ja-JP');
            let dateInfo = `<span class="date-label">作成:</span>${createdAt}`;
            if (entry.updated_at) {
                const updatedAt = new Date(entry.updated_at).toLocaleString('ja-JP');
                dateInfo += `<span class="entry-updated"><span class="date-label">最終更新:</span>${updatedAt}</span>`;
            }

            // アクションボタン（編集権限がある場合のみ表示）
            let actionButtons = '';
            if (entry.can_edit) {
                const itemsJson = JSON.stringify(entry.items || []).replace(/'/g, "\\'");
                actionButtons = `
                    <div class="action-buttons">
                        <button class="edit-btn" onclick='startEdit(${entry.id}, "${escapeHtml(entry.title)}", "${escapeHtml(entry.content)}", "${escapeHtml(entry.notes)}", ${itemsJson})'>編集</button>
                        <button class="delete-btn" onclick="deleteEntry(${entry.id})">削除</button>
                    </div>
                `;
            }

            // メモの表示（存在する場合のみ）
            let notesHtml = '';
            if (entry.notes && entry.notes.trim()) {
                notesHtml = `
                    <div class="entry-notes">
                        <span class="entry-notes-label">メモ</span>
                        <div>${escapeHtml(entry.notes)}</div>
                    </div>
                `;
            }

            // 活動項目の表示（存在する場合のみ）
            let itemsHtml = '';
            if (entry.items && entry.items.length > 0) {
                itemsHtml = `
                    <div class="entry-items">
                        <span class="items-label">活動項目</span>
                        ${entry.items.map(item => `
                            <div class="item">
                                <div class="item-name">${escapeHtml(item.item_name)}</div>
                                <div class="item-content">${escapeHtml(item.item_content)}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            entryElement.innerHTML = `
                ${actionButtons}
                <div class="entry-title">${escapeHtml(entry.title)}</div>
                <div class="entry-author">投稿者: ${escapeHtml(entry.author_name)} (@${escapeHtml(entry.author_userid)})</div>
                <div class="entry-content">${escapeHtml(entry.content)}</div>
                ${notesHtml}
                ${itemsHtml}
                <div class="entry-dates">${dateInfo}</div>
            `;
            entriesDiv.appendChild(entryElement);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('エントリーの読み込みに失敗しました');
    }
}

// 日記エントリーを削除
async function deleteEntry(id) {
    if (!confirm('本当に削除しますか？')) {
        return;
    }

    try {
        const response = await fetch(`/entries/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadEntries();
        } else {
            const data = await response.json();
            alert(data.error || '削除に失敗しました');
            if (response.status === 401) {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

// HTMLエスケープ
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
