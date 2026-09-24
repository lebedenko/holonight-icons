#include "iconrenderer.h"
#include <QGuiApplication>
#include <QDirIterator>
#include <QFile>
#include <QFileInfo>
#include <QIcon>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QPainter>
#include <QSvgRenderer>
#include <QTextStream>
#include <QTemporaryDir>
#include <stdexcept>

using Holonight::IconRenderer;
using Holonight::IconSemanticColors;
void require(bool ok, const QString &message) {
    if (!ok) throw std::runtime_error(message.toStdString());
}
QByteArray read(const QString &path) {
    QFile file(path);
    require(file.open(QIODevice::ReadOnly), "Cannot open " + path);
    return file.readAll();
}
QImage plain(const QByteArray &svg, int size) {
    QSvgRenderer renderer(svg);
    require(renderer.isValid(), "Invalid SVG");
    QImage image(size, size, QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    renderer.render(&painter);
    return image;
}
bool visible(const QImage &image) {
    for (int y=0; y<image.height(); ++y)
        for (int x=0; x<image.width(); ++x)
            if (image.pixelColor(x,y).alpha() > 20) return true;
    return false;
}
IconSemanticColors colors(QColor text) {
    return {text, QColor("#3daee9"), QColor("#27ae60"), QColor("#f67400"), QColor("#da4453")};
}
QString previewName;
int previewSize=0;
void previews(const QString &root) {
    const QList<int> sizes=previewSize?QList<int>{previewSize}:QList<int>{16,22,24,32};
    const int sample=qMax(64,previewSize*2), cell=sample+26, rowHeight=sample+36;
    for (const QString theme : {"HoloNight", "HoloNight-Dark"}) {
      for (bool darkBackground : {false, true}) {
        const QColor bg(darkBackground ? "#10131f" : "#e9eef5");
        const QColor fg(darkBackground ? "#c0caf5" : "#1f2335");
        QDirIterator places(root+'/'+theme+"/places", {"*.svg"}, QDir::Files, QDirIterator::Subdirectories);
        if (!places.hasNext())
            QTextStream(stdout)<<theme<<": Places inventory is empty; visual review resumes when SVGs are added.\n";
        QMap<QString, QStringList> families;
        QDirIterator it(root + '/' + theme, {"*.svg"}, QDir::Files, QDirIterator::Subdirectories);
        while (it.hasNext()) {
            const auto path = it.next();
            if (QFileInfo(path).isSymLink()) continue;
            const auto rel = QDir(root + '/' + theme).relativeFilePath(path);
            if (!previewName.isEmpty() && QFileInfo(path).baseName()!=previewName) continue;
            const auto family = rel.contains("/symbolic/") ? QString("symbolic") : rel.section('/',0,0);
            families[family].append(path);
        }
        for (auto f=families.begin(); f!=families.end(); ++f) {
            f.value().sort();
            for (int start=0; start<f.value().size(); start+=20) {
                const int rows=qMin(20, int(f.value().size())-start);
                QImage sheet(400+sizes.size()*2*cell, 50+rows*rowHeight, QImage::Format_ARGB32_Premultiplied);
                sheet.fill(bg);
                QPainter painter(&sheet);
                painter.setPen(fg);
                painter.drawText(10,25,theme + " / " + f.key() + (previewSize?QString(" — %1 px; then 2×").arg(previewSize):" — 16, 22, 24, 32 px; then 2×"));
                for (int row=0; row<rows; ++row) {
                    const auto path=f.value()[start+row];
                    painter.drawText(QRect(10,50+row*rowHeight,340,rowHeight-10),Qt::AlignVCenter|Qt::TextWordWrap,QFileInfo(path).baseName());
                    int col=0;
                    for (int scale : {1,2}) for (int size : sizes) {
                        const auto image=plain(read(path),size*scale);
                        require(visible(image),"Empty preview: "+path);
                        painter.drawImage(370+col*cell+(sample-image.width())/2,65+row*rowHeight+(sample-image.height())/2,image);
                        ++col;
                    }
                }
                painter.end();
                const auto out=root+"/previews/"+theme+(previewName.isEmpty()?QString():"/"+previewName)+(previewSize?QString("/%1").arg(previewSize):QString());
                QDir().mkpath(out);
                require(sheet.save(out+'/'+(darkBackground?"dark-":"light-")+f.key()+QString("-%1.png").arg(start/20+1)),"Cannot save preview");
            }
        }
    }
}
}
// Consumer-state simulation: selected surface and disabled opacity are applied
// outside the frozen SVG; renderer palette invariance is asserted separately.
QStringList folderNames(const QString &root) {
    QStringList names;
    for (const auto value : QJsonDocument::fromJson(read(root+"/../metadata/places.json")).object()["proof_names"].toArray()) {
        const auto name=value.toString();
        if (!name.endsWith("-symbolic")) names.append(name);
    }
    return names;
}
void deviceReview(const QString &root) {
    const auto names=QJsonDocument::fromJson(read(root+"/../metadata/devices.json")).object()["proof_names"].toArray();
    for (const auto value : names) for (bool symbolic : {false,true}) {
        const auto base=value.toString();
        const QList<int> sizes{16,22,24,32};
        const int cell=82, label=160, height=4*3*82+45;
        QImage sheet(label+8*cell,height,QImage::Format_ARGB32_Premultiplied);
        sheet.fill(Qt::white);
        QPainter painter(&sheet);
        painter.setPen(Qt::black);
        painter.drawText(8,24,base+(symbolic?" symbolic":" regular")+" — 16 / 22 / 24 / 32 px; 1× then 2×");
        int row=0;
        for (const QString theme : {"HoloNight", "HoloNight-Dark"}) for (bool dark : {false,true}) {
            const QColor bg(dark?"#0c1118":"#e7eef5");
            const QColor fg(dark?"#e7edf5":"#1b2533");
            for (int state=0;state<3;++state,++row) {
                const int y=40+row*82;
                const QColor surface=state==1?QColor("#385b83"):bg;
                painter.fillRect(label,y,8*cell,82,surface);
                painter.setPen(Qt::black);
                painter.drawText(QRect(4,y,label-8,82),Qt::AlignVCenter,theme+(dark?" dark ":" light ")+(state==0?"default":state==1?"selected":"disabled"));
                int col=0;
                for (int scale : {1,2}) for (int size : sizes) {
                    const auto rel=symbolic?"24/symbolic/"+base+"-symbolic.svg":QString::number(size<32?24:32)+'/'+base+".svg";
                    const auto svg=read(root+'/'+theme+"/devices/"+rel);
                    const auto icon=symbolic?IconRenderer::renderSvg(svg,{size*scale,size*scale},colors(state==1?Qt::white:fg))
                                            :plain(svg,size*scale);
                    painter.setOpacity(state==2?.45:1);
                    painter.drawImage(label+col*cell+(cell-icon.width())/2,y+(82-icon.height())/2,icon);
                    painter.setOpacity(1);
                    ++col;
                }
            }
        }
        painter.end();
        require(sheet.save(root+"/previews/"+base+(symbolic?"-symbolic-states.png":"-states.png")),"Cannot save Devices state review");
    }
}
void folderReview(const QString &root) {
    for (const QString base : folderNames(root)) for (bool symbolic : {false,true}) {
        QImage sheet(1100, 12*100+45, QImage::Format_ARGB32_Premultiplied);
        sheet.fill(Qt::white);
        QPainter painter(&sheet);
        painter.setPen(Qt::black);
        painter.drawText(12,25,base+(symbolic?" symbolic":" regular")+": 16 / 22 / 24 / 32 px, then 2x; disabled = 45% opacity");
        QImage large(1024, 600, QImage::Format_ARGB32_Premultiplied);
        large.fill(Qt::transparent);
        QPainter lp(&large);
        int row=0, panel=0;
        for (const QString theme : {"HoloNight", "HoloNight-Dark"}) {
            for (bool dark : {false,true}) {
                QColor bg(dark?"#0c1118":"#e7eef5");
                QColor fg(dark?"#e7edf5":"#1b2533");
                for (int master : {24,32}) {
                    const auto svg=read(root+'/'+theme+"/places/"+QString::number(master)+'/'+base+".svg");
                    const int y=master==24?0:300;
                    lp.fillRect(panel*256,y,256,300,bg);
                    lp.setPen(fg);
                    lp.drawText(panel*256+8,y+22,theme+QString(" / %1 px master").arg(master));
                    lp.drawImage(panel*256,y+40,plain(svg,256));
                }
                ++panel;
                for (const QString state : {"normal","selected","disabled"}) {
                    const int y=45+row*100;
                    painter.fillRect(0,y,1100,100,bg);
                    painter.setPen(fg);
                    painter.drawText(10,y+45,theme+" / "+(dark?"dark":"light")+" / "+state);
                    int col=0;
                    for (int scale : {1,2}) for (int size : {16,22,24,32}) {
                        const int x=340+col*90;
                        const auto path=symbolic?QString("24/symbolic/")+base+"-symbolic.svg":
                            QString::number(size<32?24:32)+'/'+base+".svg";
                        const auto svg=read(root+'/'+theme+"/places/"+path);
                        if (state=="selected") painter.fillRect(x,y+10,80,80,QColor(dark?"#5ea2ff":"#3e7bdb"));
                        painter.setOpacity(state=="disabled"?.45:1.0);
                        const QColor text=state=="selected"?QColor(dark?"#081018":"#ffffff"):fg;
                        painter.drawImage(x+(80-size*scale)/2,y+10+(80-size*scale)/2,
                            IconRenderer::renderSvg(svg,{size*scale,size*scale},colors(text)));
                        painter.setOpacity(1.0);
                        ++col;
                    }
                    ++row;
                }
            }
        }
        painter.end(); lp.end();
        require(sheet.save(root+"/previews/"+base+(symbolic?"-symbolic-states.png":"-states.png")),"Cannot save state review");
        if (!symbolic) require(large.save(root+"/previews/"+base+"-gradients.png"),"Cannot save gradient review");
    }
    // Compare the complete family in one readable sheet per theme/background.
    for (bool symbolic : {false,true}) for (int panel=0;panel<4;++panel) {
        const auto names=folderNames(root);
        const auto suffix=symbolic?QString("-symbolic-states.png"):QString("-states.png");
        const bool dark=panel%2;
        const QColor bg(dark?"#0c1118":"#e7eef5"), fg(dark?"#e7edf5":"#1b2533");
        QImage comparison(1100,45+100*names.size(),QImage::Format_ARGB32_Premultiplied);
        comparison.fill(bg);
        QPainter painter(&comparison);
        painter.setPen(fg);
        painter.drawText(12,25,QString(panel<2?"HoloNight":"HoloNight-Dark")+
            (dark?" / dark":" / light")+(symbolic?" / symbolic":" / regular")+
            ": 16 / 22 / 24 / 32 px, then 2x");
        for (int row=0;row<names.size();++row) {
            const QImage source(root+"/previews/"+names[row]+suffix);
            painter.drawImage(0,45+row*100,source.copy(0,45+panel*300,1100,100));
            painter.fillRect(0,45+row*100,335,100,bg);
            painter.drawText(12,100+row*100,names[row]);
        }
        painter.end();
        require(comparison.save(root+"/previews/folder-family-overview-"+QString::number(panel+1)+suffix),
                "Cannot save complete family overview");
    }
    for (const QString suffix : {"-states.png", "-symbolic-states.png", "-gradients.png"}) {
        // Paginate at two folders per sheet, preserving legible state labels.
        const auto names=folderNames(root);
        for (int first=0; first<names.size(); first+=2) {
            const QImage sample(root+"/previews/"+names[first]+suffix);
            QImage comparison(sample.width()*qMin(2,int(names.size())-first),sample.height(),QImage::Format_ARGB32_Premultiplied);
            comparison.fill(Qt::white);
            QPainter painter(&comparison);
            for (int i=first;i<qMin(first+2,int(names.size()));++i)
                painter.drawImage((i-first)*sample.width(),0,QImage(root+"/previews/"+names[i]+suffix));
            painter.end();
            require(comparison.save(root+"/previews/folder-family-"+QString::number(first/2+1)+suffix),"Cannot save folder family review");
        }
    }
}
void fallbackChecks(const QString &root) {
    QTemporaryDir temporary;
    require(temporary.isValid(), "Cannot create temporary fallback fixture");
    const auto base=temporary.path();
    for (const QString theme : {"Proof", "ControlledFallback"}) {
        QDir().mkpath(base+'/'+theme+"/places/24");
        QFile index(base+'/'+theme+"/index.theme");
        require(index.open(QIODevice::WriteOnly),"Cannot write fixture index");
        index.write(("[Icon Theme]\nName="+theme+"\nInherits="+(theme=="Proof"?"ControlledFallback":"hicolor")+"\nDirectories=places/24\n[places/24]\nSize=24\nType=Fixed\nContext=Places\n").toUtf8());
    }
    require(QFile::copy(root+"/../tests/fixtures/fixed.svg",base+"/ControlledFallback/places/24/folder-music.svg"),"Cannot create fallback icon");
    QIcon::setThemeSearchPaths({base}); QIcon::setThemeName("Proof");
    const auto inherited=QIcon::fromTheme("folder-music");
    require(!inherited.isNull() && inherited.pixmap(24,24).toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied)==plain(read(root+"/../tests/fixtures/fixed.svg"),24),"Controlled inherited lookup failed");
    require(QIcon::fromTheme("holonight-absent-custom-proof-name").isNull(),"Unexpected custom fallback");
}
// Exercise generated size metadata with temporary artwork, independent of inventory.
void placesLookupChecks(const QString &root) {
    QTemporaryDir temporary;
    require(temporary.isValid(), "Cannot create Places lookup fixture");
    const auto base=temporary.path(), theme=QString("PlacesFixture");
    const QList<int> sizes{16,20,22,24,32,48,64,96,128,256,512};
    for (int master : {24,32}) {
        const auto dir=base+'/'+theme+"/places/"+QString::number(master);
        QDir().mkpath(dir);
        QFile svg(dir+"/fixture.svg");
        require(svg.open(QIODevice::WriteOnly),"Cannot write Places master fixture");
        svg.write(QString("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 %1 %1\"><rect x=\"3\" y=\"3\" width=\"%2\" height=\"%2\" fill=\"%3\"/></svg>")
                  .arg(master).arg(master-6).arg(master==24?"#aa3311":"#1144bb").toUtf8());
    }
    for (int size : sizes) if (size!=24 && size!=32)
        require(QFile::link(QString::number(size<24?24:32),base+'/'+theme+"/places/"+QString::number(size)),"Cannot create size fixture link");
    auto index=read(root+"/HoloNight/index.theme");
    index.replace("Name=HoloNight", "Name=PlacesFixture");
    // A later generic symbolic name must not shadow the regular 24px name.
    QDir().mkpath(base+'/'+theme+"/places/24/symbolic");
    const auto symbolic=base+'/'+theme+"/places/24/symbolic/fixture-symbolic.svg";
    require(QFile::copy(root+"/../tests/fixtures/inherited.svg",symbolic),"Cannot create symbolic fixture");
    require(QFile::link("fixture-symbolic.svg",base+'/'+theme+"/places/24/symbolic/fixture.svg"),"Cannot create name alias fixture");
    QFile file(base+'/'+theme+"/index.theme");
    require(file.open(QIODevice::WriteOnly),"Cannot write Places fixture index");
    file.write(index); file.close();
    QIcon::setThemeSearchPaths({base}); QIcon::setThemeName(theme);
    for (int size : sizes) for (int scale : {1,2}) for (bool sym : {false,true}) {
        const auto icon=QIcon::fromTheme(sym?"fixture-symbolic":"fixture");
        const auto expected=plain(read(sym?symbolic:base+'/'+theme+"/places/"+QString::number(size<32?24:32)+"/fixture.svg"),size*scale);
        const auto actual=icon.pixmap(QSize(size,size),qreal(scale)).toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied);
        require(actual==expected,QString("Places fixture lookup mismatch: %1 @%2 symbolic=%3").arg(size).arg(scale).arg(sym));
    }
    QTextStream(stdout)<<"Temporary Places fixtures: all 11 display sizes at 1x/2x passed.\n";
}
void checks(const QString &root) {
    fallbackChecks(root);
    placesLookupChecks(root);
    const auto roleSvg=read(root+"/../tests/fixtures/roles.svg");
    const IconSemanticColors probes{QColor("#ff0000"), QColor("#00ff00"), QColor("#0000ff"), QColor("#ffff00"), QColor("#ff00ff")};
    const auto roleImage=IconRenderer::renderSvg(roleSvg,{24,24},probes);
    const QColor expected[] = {probes.text, probes.highlight, probes.positive, probes.neutral, probes.negative};
    for (int i=0; i<5; ++i)
        require(roleImage.pixelColor(i*4+2,12)==expected[i],"Semantic role fixture pixel mismatch");
    const auto exemptions=QJsonDocument::fromJson(read(root+"/../metadata/fixed-artwork.json")).object();
    QSet<QString> frozen;
    for (const auto entry : QJsonDocument::fromJson(read(root+"/../metadata/templates.json")).object()["templates"].toArray())
        frozen.insert(entry.toObject()["output"].toString());
    QIcon::setThemeSearchPaths({root});
    int checked=0;
    for (const QString theme : {"HoloNight", "HoloNight-Dark"}) {
        QIcon::setThemeName(theme);
        QDirIterator it(root+'/'+theme,{"*.svg"},QDir::Files,QDirIterator::Subdirectories);
        while (it.hasNext()) {
            const auto path=it.next();
            if (QFileInfo(path).isSymLink()) continue;
            const auto rel=QDir(root+'/'+theme).relativeFilePath(path);
            const bool fixed=frozen.contains(rel) || exemptions[rel].toObject()["scope"].toString()=="asset";
            const auto svg=read(path);
            for (int scale : {1,2}) for (int logical : {16,22,24,32,48,64}) {
                const int size=logical*scale;
                const auto light=IconRenderer::renderSvg(svg,{size,size},colors(QColor("#232629")));
                const auto dark=IconRenderer::renderSvg(svg,{size,size},colors(QColor("#fcfcfc")));
                // The renderer accepts resolved colors, not a QPalette or interaction state.
                const auto selected=IconRenderer::renderSvg(svg,{size,size},colors(QColor("#ffe080")));
                const auto disabled=IconRenderer::renderSvg(svg,{size,size},colors(QColor("#808080")));
                require(visible(light)&&visible(dark)&&visible(selected)&&visible(disabled),"Empty render: "+rel);
                if (fixed) {
                    require(light==dark && light==selected && light==disabled && light==plain(svg,size),"Fixed colors changed: "+rel);
                } else {
                    require(light!=dark && light!=selected && light!=disabled,"Semantic foreground did not change: "+rel);
                }
            }
            ++checked;
        }
        for (const QString name : {"go-down", "insync-alert", "drive-harddisk-symbolic"}) {
            const auto icon=QIcon::fromTheme(name);
            require(!icon.isNull(),"Qt lookup failed: "+name);
            require(visible(icon.pixmap(24,24).toImage()),"Empty Qt lookup: "+name);
        }
        for (int size : {16,20,22,24,32,48,64,96,128,256,512}) for (int scale : {1,2}) {
            QMap<QString,QString> lookups;
            for (const auto &base : folderNames(root)) {
                lookups[base]=QString::number(size<32?24:32)+'/'+base+".svg";
                lookups[base+"-symbolic"]="24/symbolic/"+base+"-symbolic.svg";
            }
            const auto aliases=QJsonDocument::fromJson(read(root+"/../metadata/places.json")).object()["lookup_aliases"].toObject();
            for (auto it=aliases.begin();it!=aliases.end();++it) {
                const auto name=QFileInfo(it.key()).baseName();
                if (it.key().contains("/symbolic/")) {
                    if (!lookups.contains(name)) lookups[name]="24/symbolic/"+it.value().toString();
                } else {
                    lookups[name]=QString::number(size<32?24:32)+'/'+it.value().toString();
                }
            }
            for (auto lookup=lookups.begin();lookup!=lookups.end();++lookup) {
                const auto name=lookup.key(), path=lookup.value();
                const auto expected=plain(read(root+'/'+theme+"/places/"+path),size*scale);
                const auto icon=QIcon::fromTheme(name);
                require(!icon.isNull(),"Missing Places lookup: "+name);
                const auto actual=icon.pixmap(QSize(size,size),qreal(scale)).toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied);
                require(actual==expected,QString("Places master lookup mismatch: %1 %2 @%3 in %4").arg(name).arg(size).arg(scale).arg(theme));
            }
        }
        const auto devices=QJsonDocument::fromJson(read(root+"/../metadata/devices.json")).object();
        QMap<QString,QString> deviceNames;
        for (const auto value : devices["proof_names"].toArray()) {
            const auto base=value.toString();
            deviceNames[base]=base;
            deviceNames[base+"-symbolic"]=base+"-symbolic";
        }
        const auto deviceAliases=devices["lookup_aliases"].toObject();
        for (auto it=deviceAliases.begin();it!=deviceAliases.end();++it) {
            if (it.key().contains("/symbolic/") && !it.key().endsWith("-symbolic.svg")) continue;
            deviceNames[QFileInfo(it.key()).baseName()]=QFileInfo(it.value().toString()).baseName();
        }
        for (int size : {16,20,22,24,32,48,64,96,128,256,512}) for (int scale : {1,2}) {
            for (auto it=deviceNames.begin();it!=deviceNames.end();++it) {
                const bool symbolic=it.key().endsWith("-symbolic");
                const auto rel=symbolic ? "24/symbolic/"+it.value()+".svg"
                                        : QString::number(size<32?24:32)+'/'+it.value()+".svg";
                const auto expected=plain(read(root+'/'+theme+"/devices/"+rel),size*scale);
                const auto icon=QIcon::fromTheme(it.key());
                require(!icon.isNull(),"Missing Devices lookup: "+it.key());
                const auto actual=icon.pixmap(QSize(size,size),qreal(scale)).toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied);
                require(actual==expected,QString("Devices master lookup mismatch: %1 %2 @%3 in %4").arg(it.key()).arg(size).arg(scale).arg(theme));
            }
        }
        // High-resolution alpha bounds include strokes and fractional coverage.
        QStringList masterPaths;
        for (const auto &name : folderNames(root))
            masterPaths << "24/"+name+".svg" << "32/"+name+".svg" << "24/symbolic/"+name+"-symbolic.svg";
        for (const auto &rel : masterPaths) {
            const int native=rel.startsWith("32/")?32:24, factor=100;
            const auto rendered=plain(read(root+'/'+theme+"/places/"+rel),native*factor);
            if (rel == "24/symbolic/folder-symbolic.svg")
                require(rendered.pixelColor(native*factor/2,native*factor/2).alpha()==0,
                        "Symbolic folder interior must remain transparent");
            int left=rendered.width(), right=-1, top=rendered.height(), bottom=-1;
            for (int y=0;y<rendered.height();++y) for (int x=0;x<rendered.width();++x) {
                if (rendered.pixelColor(x,y).alpha()>0) {
                    left=qMin(left,x); right=qMax(right,x); top=qMin(top,y); bottom=qMax(bottom,y);
                }
            }
            require(left>=2*factor && top>=2*factor && right<(native-2)*factor && bottom<(native-2)*factor,
                    QString("Places painted bounds exceed safe area: %1, left=%2 right=%3 top=%4 bottom=%5")
                        .arg(rel).arg(left).arg(right).arg(top).arg(bottom));
            if (!rel.contains("symbolic"))
                require(qAbs((right-left+1)-((native-4)*factor))<=2,
                        QString("Places painted width mismatch: %1, left=%2 right=%3").arg(rel).arg(left).arg(right));
        }
        // Confirm status badge colors, not only foreground changes.
        for (const QString name : {"insync-alert", "insync-synced"}) {
            const auto svg=read(root+'/'+theme+"/status/24/"+name+".svg");
            auto changed=colors(Qt::black);
            const auto before=IconRenderer::renderSvg(svg,{48,48},changed);
            changed.neutral=QColor("#aa00ff"); changed.positive=QColor("#00ffff");
            require(before!=IconRenderer::renderSvg(svg,{48,48},changed),"Status role not recolored: "+name);
        }
    }
    QTextStream(stdout)<<"Rendered "<<checked<<" masters through holonight-qt at 12 sizes/scales and 4 palettes; fixed colors and Qt lookup passed.\n";
}
int main(int argc,char **argv) {
    QGuiApplication app(argc,argv);
    try {
        require(argc>=2,"Usage: render-check BUILD [--previews]");
        const auto root=QDir(QString::fromLocal8Bit(argv[1])).absolutePath();
        for (int i=3;i<argc;++i) {
            const QString option=QString::fromLocal8Bit(argv[i]);
            require(i+1<argc,"Missing preview option value");
            if(option=="--name") previewName=QString::fromLocal8Bit(argv[++i]);
            else if(option=="--size") previewSize=QString::fromLocal8Bit(argv[++i]).toInt();
            else require(false,"Unknown preview option");
        }
        if (argc>2 && QString::fromLocal8Bit(argv[2])=="--previews") { previews(root); folderReview(root); deviceReview(root); }
        else checks(root);
    } catch (const std::exception &error) {
        QTextStream(stderr)<<error.what()<<'\n'; return 1;
    }
}
