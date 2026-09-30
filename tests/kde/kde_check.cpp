#include <KIconLoader>
#include <KIconTheme>
#include <QGuiApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QImage>
#include <QPainter>
#include <QPalette>
#include <QStandardPaths>
#include <QSvgRenderer>
#include <QTextStream>
#include <stdexcept>

static void check(bool ok, const QString &message)
{
    if (!ok) throw std::runtime_error(message.toStdString());
}
static QByteArray read(const QString &path)
{
    QFile file(path);
    check(file.open(QIODevice::ReadOnly), "Cannot read " + path);
    return file.readAll();
}
static void write(const QString &path, const QByteArray &data)
{
    QFile file(path);
    check(file.open(QIODevice::WriteOnly), "Cannot write " + path);
    check(file.write(data) == data.size(), "Incomplete write: " + path);
}
static QImage plain(const QByteArray &svg, int pixels)
{
    QSvgRenderer renderer(svg);
    check(renderer.isValid(), "Invalid SVG");
    QImage image(pixels, pixels, QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    renderer.render(&painter);
    return image;
}
static int countColor(const QImage &image, QColor color)
{
    int count = 0;
    for (int y = 0; y < image.height(); ++y)
        for (int x = 0; x < image.width(); ++x)
            if (image.pixelColor(x, y) == color) ++count;
    return count;
}
// Thin glyphs scaled to 24px may have no fully covered pixel. Accept pixels
// on the paper-to-glyph antialiasing ramp, with at least 50% glyph coverage.
static int countGlyph(const QImage &image, QColor paper, QColor glyph)
{
    const double dr = glyph.red()-paper.red(), dg = glyph.green()-paper.green(), db = glyph.blue()-paper.blue();
    const double length = dr*dr + dg*dg + db*db;
    if (length < 1) return 0;
    int count = 0;
    for (int y=0; y<image.height(); ++y) for (int x=0; x<image.width(); ++x) {
        const auto c = image.pixelColor(x,y);
        if (qAbs(c.alpha() - paper.alpha()) > 1 || c.alpha() == 0) continue;
        const double r=c.red()-paper.red(), g=c.green()-paper.green(), b=c.blue()-paper.blue();
        const double coverage=(r*dr+g*dg+b*db)/length;
        if (coverage < .5 || coverage > 1.01) continue;
        const double er=r-coverage*dr, eg=g-coverage*dg, eb=b-coverage*db;
        if (er*er+eg*eg+eb*eb < 9) ++count;
    }
    return count;
}
int main(int argc, char **argv)
{
    QGuiApplication app(argc, argv);
    try {
        check(argc == 3, "Usage: kde-check SVG OUTPUT_DIRECTORY");
        const auto svg = read(QString::fromLocal8Bit(argv[1]));
        const QString output = QString::fromLocal8Bit(argv[2]);
        const QString themeName = "HoloNightNativeKdeProof";
        const QString theme = QStandardPaths::writableLocation(QStandardPaths::GenericDataLocation)
            + "/icons/" + themeName;
        check(QDir().mkpath(theme + "/32/mimetypes"), "Cannot create isolated theme");
        write(theme + "/index.theme", "[Icon Theme]\nName=HoloNight native KDE proof\n"
              "FollowsColorScheme=true\nDirectories=32/mimetypes\n"
              "ScaledDirectories=32/mimetypes/.\n"
              "[32/mimetypes]\nSize=32\nType=Scalable\nMinSize=16\nMaxSize=64\nContext=MimeTypes\n"
              "[32/mimetypes/.]\nSize=32\nScale=2\nType=Scalable\nMinSize=16\nMaxSize=64\nContext=MimeTypes\n");
        const auto iconPath = theme + "/32/mimetypes/application-xml.svg";
        write(iconPath, svg);
        auto control = svg;
        control.replace("id=\"current-color-scheme\"", "id=\"fallback-colors\"");
        check(control != svg, "Prototype must have a current-color-scheme stylesheet");
        write(theme + "/32/mimetypes/proof-control.svg", control);
        // Independent solid regions make palette-role mapping unambiguous.
        write(theme + "/32/mimetypes/proof-roles.svg", R"SVG(<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<style id="current-color-scheme" type="text/css">
.ColorScheme-Text {color:#123456;} .ColorScheme-Accent {color:#234567;} .ColorScheme-Highlight {color:#345678;}
</style>
<path class="ColorScheme-Text" fill="currentColor" d="M0 0h8v32H0z"/>
<path class="ColorScheme-Accent" fill="currentColor" d="M8 0h8v32H8z"/>
<path class="ColorScheme-Highlight" fill="currentColor" d="M16 0h8v32H16z"/>
<path fill="#000000" opacity="0.2" d="M24 0h8v16h-8z"/>
<path fill="#ffffff" opacity="0.2" d="M24 16h8v16h-8z"/>
</svg>)SVG");
        write(theme + "/32/mimetypes/proof-fresh.svg", read(theme + "/32/mimetypes/proof-roles.svg"));
        KIconTheme::forceThemeForTests(themeName);
        KIconLoader loader;
        check(loader.theme() && loader.theme()->internalName() == themeName
              && loader.theme()->followsColorScheme(), "KDE did not load the isolated recolorable theme");
        auto render = [&](const QString &name, int size, int scale, int state) {
            QString resolved;
            const auto pixmap = loader.loadScaledIcon(name, KIconLoader::Desktop, qreal(scale),
                QSize(size, size), state, {}, &resolved, true);
            check(!pixmap.isNull(), "KDE failed to render " + name);
            check(QFileInfo(resolved).canonicalFilePath().startsWith(QFileInfo(theme).canonicalFilePath() + '/'),
                  "Icon escaped the isolated theme: " + resolved);
            const auto image = pixmap.toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied);
            check(image.size() == QSize(size * scale, size * scale), "Wrong native output dimensions");
            return image;
        };
        QImage sheet(1000, 720, QImage::Format_ARGB32_Premultiplied);
        sheet.fill(QColor("#20252b"));
        QPainter painter(&sheet);
        painter.setPen(Qt::white);
        painter.drawText(20, 25, QString("Native KIconLoader — KF %1 / Qt %2").arg(KDE_ICON_THEMES_VERSION, qVersion()));
        painter.drawText(20, 48, "Columns: 24px @1x | 24px @2x | 32px @1x | 32px @2x | enlarged 32px @2x");
        int row = 0, renders = 0;
        QStringList failures;
        for (bool dark : {false, true}) {
            QPalette palette;
            const QColor text(dark ? "#e7edf5" : "#202630");
            const QColor background(dark ? "#10151c" : "#f0f3f7");
            const QColor accent("#d52be8"), highlight("#167345"), selectedText("#ffffff");
            for (auto group : {QPalette::Active, QPalette::Inactive, QPalette::Disabled}) {
                palette.setColor(group, QPalette::WindowText, text);
                palette.setColor(group, QPalette::Window, background);
                palette.setColor(group, QPalette::Base, background);
                palette.setColor(group, QPalette::Text, text);
                palette.setColor(group, QPalette::Accent, accent);
                palette.setColor(group, QPalette::Highlight, highlight);
                palette.setColor(group, QPalette::HighlightedText, selectedText);
            }
            loader.setCustomPalette(palette);
            const auto normal = render("proof-roles", 32, 1, KIconLoader::DefaultState);
            check(normal.pixelColor(4, 8) == text, "KDE Text role mismatch");
            check(normal.pixelColor(12, 8) == accent, "KDE Accent unsupported or mapped incorrectly");
            check(normal.pixelColor(20, 8) == highlight, "KDE Highlight role mismatch");
            check(normal.pixelColor(28, 8) == QColor(0, 0, 0, 51)
                  && normal.pixelColor(28, 24) == QColor(255, 255, 255, 51), "KDE changed fixed shading paints");
            check(render("proof-control", 32, 1, KIconLoader::DefaultState) == plain(control, 32),
                  "Negative control unexpectedly recolored");
            for (int state : {int(KIconLoader::DefaultState), int(KIconLoader::SelectedState), int(KIconLoader::DisabledState)}) {
                const QString stateName = state == KIconLoader::DefaultState ? "normal" :
                    state == KIconLoader::SelectedState ? "selected" : "disabled";
                const auto roles = render("proof-roles", 32, 1, state);
                const auto paper = roles.pixelColor(4, 8), glyph = roles.pixelColor(12, 8);
                if (state == KIconLoader::SelectedState) {
                    check(paper == selectedText, "Selected Text did not become highlighted text");
                    check(roles.pixelColor(20, 8) == selectedText, "Selected Highlight mapping changed");
                    check(glyph != paper, "Selected Accent collapsed into paper color");
                }
                const int top = 65 + row * 106;
                painter.fillRect(10, top, 980, 100, state == KIconLoader::SelectedState ? highlight : background);
                painter.setPen(state == KIconLoader::SelectedState ? selectedText : text);
                painter.drawText(20, top + 23, (dark ? "Dark / " : "Light / ") + stateName);
                int col = 0;
                for (int size : {24, 32}) for (int scale : {1, 2}) {
                    const auto image = render("application-xml", size, scale, state);
                    check(countColor(image, paper) > 0 && countGlyph(image, paper, glyph) > 0,
                          QString("Prototype lacks KDE paper/glyph colors in %1 at %2px @%3: paper %4 (%5 pixels), glyph %6 (%7 pixels)").arg(stateName).arg(size).arg(scale).arg(paper.name()).arg(countColor(image,paper)).arg(glyph.name()).arg(countColor(image,glyph)));
                    if (state == KIconLoader::DefaultState) {
                        const auto fallback = plain(svg, size * scale);
                        for (int y = 0; y < image.height(); ++y) for (int x = 0; x < image.width(); ++x)
                            check(image.pixelColor(x,y).alpha() == fallback.pixelColor(x,y).alpha(),
                                  "Native recoloring changed geometry/opacity");
                    }
                    const auto filename = QString("%1-%2-%3px-%4x.png").arg(dark ? "dark" : "light", stateName).arg(size).arg(scale);
                    check(image.save(output + '/' + filename), "Cannot save " + filename);
                    painter.drawImage(QPoint(220 + col * 145, top + (100-image.height())/2), image);
                    if (size == 32 && scale == 2) painter.drawImage(QRect(855, top + 2, 96, 96), image);
                    ++col;
                    ++renders;
                }
                ++row;
            }
            // Reuse the same loader/name after changing only Accent to expose stale palette caches.
            palette.setColor(QPalette::Accent, QColor("#00bddd"));
            loader.setCustomPalette(palette);
            const auto refreshedAccent = render("proof-roles", 32, 1, KIconLoader::DefaultState).pixelColor(12, 8);
            check(render("proof-fresh", 32, 1, KIconLoader::DefaultState).pixelColor(12, 8) == QColor("#00bddd"),
                  "Accent-only palette change failed even for an uncached icon name");
            if (refreshedAccent != QColor("#00bddd"))
                failures.append(QString("%1: accent-only palette change returned %2; expected #00bddd")
                                .arg(dark ? "dark" : "light", refreshedAccent.name()));
        }
        painter.end();
        check(sheet.save(output + "/comparison.png"), "Cannot save comparison sheet");
        QString report = QString("Native KIconLoader recoloring checks\nKIconThemes: %1\nQt: %2\nInput: %3\n"
            "%4 prototype renders: light/dark, normal/selected/disabled, 24/32px, 1x/2x.\n"
            "Passed: independent Text/Accent/Highlight roles, selected separation, fixed shading,\n"
            "negative control, geometry/opacity, isolated lookup.\n"
            "24px scales the supplied 32px prototype; this is not an authored 24px master test.\n"
            "Desktop color-change propagation and Dolphin integration are not tested.\n")
            .arg(KDE_ICON_THEMES_VERSION, qVersion(), QFileInfo(QString::fromLocal8Bit(argv[1])).absoluteFilePath()).arg(renders);
        report += failures.isEmpty() ? "PASS: accent-only palette refresh.\nOverall: PASS\n"
            : "FAIL: " + failures.join("\nFAIL: ") + "\nOverall: FAIL (native palette cache refresh)\n";
        write(output + "/report.txt", report.toUtf8());
        QTextStream(stdout) << report;
        return failures.isEmpty() ? 0 : 1;
    } catch (const std::exception &error) {
        QTextStream(stderr) << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
