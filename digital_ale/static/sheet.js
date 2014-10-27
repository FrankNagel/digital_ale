var SheetIdent = function() {
    this.country = '';
    this.question = '';
}

var SheetDataRow = function() {
    this.code = '';
    this.transcription = '';
    this.comment = ''
    this.city_codes = '';
}

var AleSheet = function() {
    this.ident = new SheetIdent;
    this.info = []; //nearly always two lines with extended country and question information
    this.data_rows = []; // list of SheetDataRow
    this.comment_lines = [];
}

var ParseResult = function() {
    this.success = true;
    this.errors = [];
    this.sheet = new AleSheet();
}

function parse_sheet_entry(entry) {
    var part_re = /\(\s*[1-4]\s*\.\s*[a-zA-Z]+\s*\)/;
    var result = new ParseResult();
    
    entry = entry.trim();
    var parts = entry.split(part_re);
    parts.shift() //ignore stuff before '(1.IDENT)'
    if (parts.length < 3) {
        result.errors.push("Expecting at least 3 parts: (1.IDENT), (2.INFO), (3.DATA)");
        result.success = false;
    }
    try {
        parse_ident(parts.shift(), result);
    } catch (err) {
        result.errors.push("Internal Error parsing (1.IDENT): " + err);
        result.success = false;
    };
    try {
        parse_information(parts.shift(), result);
    } catch (err) {
        result.errors.push("Internal Error parsing (2.DATA): " + err);
        result.success = false;
    };
    try {
        parse_data(parts.shift(), result);
    } catch (err) {
        result.errors.push("Internal Error parsing (3.DATA): " + err);
        result.success = false;
    };
    try {
        parse_comment(parts.shift(), result);
    } catch (err) {
        result.errors.push("Internal Error parsing (4.KOM): " + err);
        result.success = false;
    };

    return result;
}

function parse_ident(entry, result) {
    if (entry === undefined) return;
    var parts = entry.trim().split(/\n|\r|\r\n/);
    if (parts.length !== 2) {
        result.errors.push("(1.IDENT): Expecting two entries in separate lines. Found " + parts.length + 
                           " lines with entries.");
        result.success = false;
        return;
    }
    result.sheet.ident.country = parts[0].replace('<u>', '').replace('</u>', '');
    result.sheet.ident.question = parts[1].replace('<u>', '').replace('</u>', '');
}

function parse_information(entry, result) {
    if (entry === undefined) return;
    result.sheet.info = entry.trim().split(/\n|\r|\r\n/);
}

function parse_data(entry, result) {
    if (entry === undefined) return;
    var parts = entry.trim().split(/\n|\r|\r\n/);
    for (var index = 0; index < parts.length; index++) {
        part = parts[index];
        columns = part.split(/\t/);
        if (columns.length == 3) { //assume comment column missing
            columns.splice(3, 0, '');
        }
        if (columns.length != 4) {
            result.errors.push("(3.DATA): Expecting four columns in line " + index + ': ' + part);
            result.success = false;
            continue;
        }
        var row = new SheetDataRow();
        result.sheet.data_rows.push(row);
        row.code = columns[0];
        row.transcription = columns[1];
        row.comment = columns[2];
        row.city_codes = columns[3];
    }
}

function parse_comment(entry, result) {
    if (entry === undefined) return;
    result.sheet.comment_lines = entry.trim().split(/\n|\r|\r\n/);
}


function render_sheet(sheet, canvas) {
    var line_height = 22;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = "#0000FF";
    ctx.font = "12pt Arial";

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    //indent
    ctx.fillText(sheet.ident.country, 720, 230);
    ctx.fillText(sheet.ident.question, 720, 250);

    //information
    y_pos = 250;
    for (var index = 0; index < sheet.info.length; index++) {
        ctx.fillText(sheet.info[index], 140, y_pos);
        y_pos += line_height;
    }

    //data rows
    y_pos = Math.max(y_pos+10, 310)
    for (var index = 0; index < sheet.data_rows.length; index++) {
        var data_row = sheet.data_rows[index];
        ctx.fillText(data_row.code, 75, y_pos);
        var y_pos_trans = render_line_wrapped(data_row.transcription, ctx, 140, 390, y_pos, line_height)
        if (data_row.comment !== '') {
            y_pos_trans = render_line_wrapped(data_row.comment, ctx, 140, 390, y_pos_trans, line_height)
        }
        var y_pos_codes = render_line_wrapped(data_row.city_codes, ctx, 410, 760, y_pos, line_height)
        
        y_pos = Math.max(y_pos_trans, y_pos_codes) + 10;
    }

    y_pos += 20;
    //comment lines
    for (var index = 0; index < sheet.comment_lines.length; index++) {
        y_pos = render_line_wrapped(sheet.comment_lines[index], ctx, 140, 760, y_pos, line_height);
        y_pos += 5;
    }
}

var decodeEntities = (function() {
  // this prevents any overhead from creating the object each time
  var element = document.createElement('div');

  function decodeHTMLEntities (str) {
    if(str && typeof str === 'string') {
      element.innerHTML = str;
      str = element.textContent;
      element.textContent = '';
    }

    return str;
  }

  return decodeHTMLEntities;
})();

var UnderlineRenderer = function(ctx) {
    this.ctx = ctx;
    this.regions = [];
    this.start = undefined;
    this.tmp_end = undefined;

    this.strip_tags = function(word) {
        return word.replace(/<u\s*>/g, "").replace(/<\/u\s*>/g, "");
    }

    this.analyse = function(line, word) {
        var pattern;
        var offset = this.ctx.measureText(line).width;
        while (true) {
            pattern = this.start === undefined && /<u\s*>/ || /<\/u\s*>/ ;
            var index = word.search(pattern);
            if (index !== -1) {
                tail = word.slice(index);
                index2 = tail.search('>');
                tail = tail.slice(index2+1);
                if (this.start === undefined) {
                    this.start = offset + this.ctx.measureText(word.slice(0, index)).width;
                    this.tmp_end = offset + this.start + this.ctx.measureText(tail).width;
                } else {
                    this.regions.push(this.start);
                    this.regions.push(offset + this.ctx.measureText(word.slice(0, index)).width);
                    this.start = undefined;
                }
                console.debug(tail);
                console.debug(this.regions);
                word = tail;
            } else {
                break;
            }
        }
    }

    this.render = function(x, y) {
        if (this.start !== undefined) {
            this.regions.push(start);
            this.regions.push(tmp_end);
            this.start = 0;
        }
        for (var i=0; i < this.regions.length; i+=2) {
            this.ctx.beginPath();
            this.ctx.moveTo(x + this.regions[i], y);
            this.ctx.lineTo(x + this.regions[i+1], y);
            this.ctx.stroke();
        }
        this.regions = [];
    }
}

function render_line_wrapped(line, ctx, x_start, x_end, y_start, line_height) {
    var y_pos = y_start;
    var width = x_end - x_start;
    var words = line.split(' ');
    var render_line = '';
    var underline = new UnderlineRenderer(ctx);

    line = decodeEntities(line);
    for(var n = 0; n < words.length; n++) {
        var test_line = render_line + underline.strip_tags(words[n]);
        var metrics = ctx.measureText(test_line);
        var test_width = metrics.width;
        if (test_width > width && n > 0) {
            ctx.fillText(render_line, x_start, y_pos);
            underline.render(x_start, y_pos+4);
            render_line = underline.strip_tags(words[n] + ' ');
            underline.analyse('', render_line);
            y_pos += line_height;
        }
        else {
            underline.analyse(render_line, words[n]);
            render_line = test_line + ' ';
        }
    }
    ctx.fillText(render_line, x_start, y_pos);
    underline.render(x_start, y_pos+4);
    return y_pos + line_height;
}

function refresh_canvas() {
    var entry = $('#sheet_text').val();
    var parse_result = parse_sheet_entry(entry);
    render_sheet(parse_result.sheet, document.getElementById('canvas'));
}

$(function() {
    $("#slider-vertical").slider({
        orientation: "vertical",
        range: "max",
        min: 0,
        max: 100,
        value: 85,
        slide: function( event, ui ) {
            document.getElementById('ale-scan').style.height = (100 - ui.value)+'%'; 
        }
    });
    document.getElementById('ale-scan').style.height = (100 - $("#slider-vertical").slider("value"))+'%';
    
    $("#refresh").click(refresh_canvas);
    refresh_canvas();

    $('#canvas').draggable();

    //make TAB usable in textarea
    $(document).delegate('#sheet_text', 'keydown', function(e) {
        var keyCode = e.keyCode || e.which;
        
        if (keyCode == 9) {
            e.preventDefault();
            var start = $(this).get(0).selectionStart;
            var end = $(this).get(0).selectionEnd;
            
            // set textarea value to: text before caret + tab + text after caret
            $(this).val($(this).val().substring(0, start)
                        + "\t"
                        + $(this).val().substring(end));
            
            // put caret at right position again
            $(this).get(0).selectionStart =
                $(this).get(0).selectionEnd = start + 1;
        }
    });
    $('#rotate').click(function() {
        $('#ale-scan-bg').toggleClass('rotated');
    });
});
