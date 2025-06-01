import { MeasurementLinesManager } from './measurement_lines_manager.js';

export function positionCanvasObjects(canvas, wallWidth) {
    const scale = canvas.width / wallWidth;
    document.querySelectorAll('.canvas-object').forEach(div => {
        const x = parseFloat(div.getAttribute('data-x')) * scale;
        const y = parseFloat(div.getAttribute('data-y')) * scale;
        const width = parseFloat(div.getAttribute('data-width')) * scale;
        const height = parseFloat(div.getAttribute('data-height')) * scale;
        div.style.left = x + 'px';
        div.style.top = y + 'px';
        div.style.width = width + 'px';
        div.style.height = height + 'px';
        div.style.lineHeight = height + 'px';
        div.style.textAlign = 'center';
    });
}

export function makeObjectsDraggable(canvas, wallWidth, wallHeight, measurementManager) {
    const scale = canvas.width / wallWidth;
    document.querySelectorAll('.canvas-object').forEach(obj => {
        obj.style.zIndex = '2';
    });

    interact('.canvas-object').draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent',
                endOnly: true
            })
        ],
        listeners: {
            start: function(event) {
                measurementManager.clearMeasurementLines();
                event.target.style.zIndex = '3';
            },
            move: function(event) {
                const target = event.target;
                let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / scale;
                let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / scale;
                const width = parseFloat(target.getAttribute('data-width'));
                const height = parseFloat(target.getAttribute('data-height'));

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
                positionCanvasObjects(canvas, wallWidth);
                updateObjectPosition(target.id.replace('object-', ''), x, y);

                measurementManager.drawMeasurementLines(x, y, width, height, scale, canvas, wallWidth, wallHeight);
            },
            end: function(event) {
                measurementManager.clearMeasurementLines();
                event.target.style.zIndex = '2';
            }
        }
    });
}

function updateObjectPosition(objId, x, y) {
    fetch(`/update_object_position/${objId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ x: x, y: y })
    });
}