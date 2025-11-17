/// <reference types="p5/global" />

/* //TODO:
 - Necesitamos agarrar los datos especificos de cada conjunto y decidir que conjuntos habra y agregar cada uno para cargarlo en CalculateBaseSets() (MEJOR SI es en otro archivo)
 - Crear el sistema de logica para unir los datos, operaciones union, interseccion, 
 - Hacer que al juntar las dos celulas(conjuntos) se elimienn y se cree una nueva con la informacion nueva dependiendo de la operacion previamente hecha
 - colocar 3 simbolos de herramientas en la barra para decidir que operaciones se hara entre los conjuntos cuando los arrastremos unos a otros
    

 */
let cells = [];
let data;
let draggingCell = null;
let baseSets = {}

let worldView = {
    x: 0,
    y: 0,
    zoom: 1,
    minZoom: 0.75,
    maxZoom: 1.5
};

let isPanning = false;
let worldMouseX = 0;
let worldMouseY = 0;


async function preload() {
    data = await d3.csv("data/titanic.csv");
    console.log("datos cargados", data);
}

function setup() {
    createCanvas(windowWidth, windowHeight)
    cells.push(new Cell(200, 300, 80, color(255, 100, 100), "Mujeres", 240));
    cells.push(new Cell(400, 300, 90, color(100, 100, 255), "1ra Clase", 120));



    // ESTA NO VA A SER LA LOGICA PARA crear LOS CONJUNTOS ES SOLO PRUEBA
    baseSets['Set Prueba 1'] = {
        count: 100,
        color: color(255, 0, 0), 
        name: "Set Prueba 1"
    };
    baseSets['Set Prueba 2'] = {
        count: 200,
        color: color(0, 0, 255), 
        name: "Set Prueba 2"
    };
    baseSets['Otro'] = {
        count: 50,
        color: color(0, 255, 0), 
        name: "Otro"
    };

    calculateBaseSets(); // donde hacemos nuestros conjuntos
    setupPalette();
    //createCanvas()

    worldView.x = width / 2;
    worldView.y = height / 2;
};

function draw() {
    background(250);

    translate(worldView.x, worldView.y);
    scale(worldView.zoom);

    worldMouseX = (mouseX - worldView.x) / worldView.zoom;
    worldMouseY = (mouseY - worldView.y) / worldView.zoom;

    drawGrid();

    for (let cell of cells) {
        cell.update(); 
        cell.show();   
    }
};

function drawGrid() {
    let gridSize = 40;
    stroke(240);
    strokeWeight(2);

    let i = 10000 //  para que el grid sea grande

    for (let x = -i; x <= i; x += gridSize) {
        line(x, -i, x, i);
    }

    for (let y = -i; y <= i; y += gridSize) {
        line(-i, y, i, y);
    }
}

function mousePressed() {
    draggingCell = null;

    for (let i = cells.length - 1; i >= 0; i--) {
      let cell = cells[i];
      if (cell.isMouseOver()) {
        draggingCell = cell; 
        cell.startDrag();
        isPanning = false
        break;
      }
    }

    isPanning = true;
  }

function mouseDragged() {
    if (isPanning && !draggingCell) {
        let moveX = (mouseX - pmouseX) * 0.4;
        let moveY = (mouseY - pmouseY) * 0.4;

        worldView.x += moveX; 
        worldView.y += moveY;
    }
}

function mouseReleased() {
    if (draggingCell) {
      draggingCell.stopDrag();
      draggingCell = null;
    }
    isPanning = false;
}

function calculateBaseSets() {
    if (!data) {
        console.error("Los datos no se cargaron");
        return; 
    }
}

function setupPalette() {
    const topBar = document.getElementById('top-bar');
    const expandBtn = document.getElementById('expand-btn');
    const palette = document.getElementById('set-palette');

    if (!topBar || !expandBtn || !palette) {
        console.error("faltan elementos");
        return; 
    }

    // --- Lógica del Botón de Expandir ---
    expandBtn.addEventListener('click', () => {
        // "toggle" añade la clase si no está, o la quita si ya está
        topBar.classList.toggle('expanded');
    });

    // 
    palette.innerHTML = ''; 
    for (const setName in baseSets) {
        const set = baseSets[setName];
        
        let li = document.createElement('li');
        li.className = 'set-item';
        
        li.innerHTML = `<span class="set-name">${set.name}</span>`;
        
        // Evento de click para crear el conjunto
        li.addEventListener('click', () => {
            console.log(`click ${set.name}`);

            let randomScreenX = random(width * 0.2, width * 0.8);
            let randomScreenY = random(height * 0.4, height * 0.8);

            let newCellWorldX = (randomScreenX - worldView.x) / worldView.zoom;
            let newCellWorldY = (randomScreenY - worldView.y) / worldView.zoom;
            
            let newCell = new Cell(
                newCellWorldX, 
                newCellWorldY, 
                80, 
                set.color,
                set.name
            );
            
            newCell.count = set.count; 
            cells.push(newCell);
            
        });
        
        palette.appendChild(li);
    }
}
    
function mouseWheel(event) {
    let zoomFactor = 1.05;
    let newZoom;

    if (event.deltaY < 0) {
        newZoom = worldView.zoom * zoomFactor; // Zoom In
    } else {
        newZoom = worldView.zoom / zoomFactor; // Zoom Out
    }
    
    newZoom = constrain(newZoom, worldView.minZoom, worldView.maxZoom);

    let worldX = (mouseX - worldView.x) / worldView.zoom;
    let worldY = (mouseY - worldView.y) / worldView.zoom;

    worldView.x = mouseX - worldX * newZoom;
    worldView.y = mouseY - worldY * newZoom;
    worldView.zoom = newZoom;

    // Previene que la página web haga scroll
    return false;
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
