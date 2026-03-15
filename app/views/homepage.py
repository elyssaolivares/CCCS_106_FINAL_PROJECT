import flet as ft
import threading
import time

def homepage(page, login_func):

    _alive = True

    def get_started_clicked(e):
        nonlocal _alive
        _alive = False
        login_func(page)

    def on_hover(e):
        if e.data == "true":
            btn_container.scale = 1.05
            btn_container.border = ft.border.all(2, ft.Colors.WHITE)
        else:
            btn_container.scale = 1.0
            btn_container.border = ft.border.all(1.5, ft.Colors.with_opacity(0.6, ft.Colors.WHITE))
        page.update()

    btn_container = ft.Container(
        content=ft.Text("GET STARTED", size=14, font_family="Poppins-SemiBold", color=ft.Colors.WHITE),
        width=200,
        height=48,
        bgcolor=ft.Colors.TRANSPARENT,
        border=ft.border.all(1.5, ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
        border_radius=8,
        alignment=ft.alignment.center,
        on_click=get_started_clicked,
        on_hover=on_hover,
        scale=1.0,
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # === LOGO — starts big, will shrink in place ===
    home_logo = ft.Image(
        src="/cspc_logo.png",
        width=180,
        height=180,
        fit=ft.ImageFit.CONTAIN,
        animate_size=ft.Animation(1200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # Top spacer — starts tall to push logo to center, shrinks to 0
    top_spacer = ft.Container(
        height=250,
        animate_size=ft.Animation(1200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # Bottom spacer — counterbalances, starts tall, shrinks to 0
    bottom_spacer = ft.Container(
        height=250,
        animate_size=ft.Animation(1200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # === HOMEPAGE TEXT (starts invisible) ===
    welcome_text = ft.Text(
        "Welcome to", size=13,
        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
        font_family="Poppins-Light",
        text_align=ft.TextAlign.CENTER,
        opacity=0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
    )

    fixit_title = ft.Text(
        "FIXIT", size=60,
        font_family="Poppins-Bold",
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
        opacity=0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
    )

    subtitle = ft.Text(
        "Faculty Issue eXchange and\nInformation Tracker",
        size=12,
        color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
        font_family="Poppins-Light",
        text_align=ft.TextAlign.CENTER,
        opacity=0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
    )

    btn_wrapper = ft.Container(
        content=btn_container,
        opacity=0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
    )

    # Background — uses DecorationImage to guarantee full coverage on any screen
    bg = ft.Container(
        expand=True,
        image=ft.DecorationImage(
            src="/bg.jpg",
            fit=ft.ImageFit.COVER,
        ),
        scale=1.25,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(12000, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(12000, ft.AnimationCurve.EASE_IN_OUT),
    )

    bg_overlay = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.45, "#0A1628"),
        expand=True,
    )

    # Dark cover — hides bg initially, fades away
    dark_cover = ft.Container(
        bgcolor="#0A1628",
        expand=True,
        opacity=1,
        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
    )

    # Column: spacer pushes logo to center initially
    content_column = ft.Column(
        [
            top_spacer,
            home_logo,
            ft.Container(height=10),
            welcome_text,
            fixit_title,
            subtitle,
            ft.Container(height=25),
            btn_wrapper,
            bottom_spacer,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        scroll=ft.ScrollMode.HIDDEN,
    )

    content_layer = ft.Container(
        content=content_column,
        alignment=ft.alignment.center,
        expand=True,
    )

    main_stack = ft.Stack(
        [bg, bg_overlay, dark_cover, content_layer],
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    page.controls.clear()
    page.add(main_stack)
    page.update()

    # === ANIMATION SEQUENCE ===
    def run_intro():
        # Phase 1: Big logo centered on dark screen
        time.sleep(1.4)

        # Phase 2: Shrink logo + collapse spacers (logo slides up to final pos)
        home_logo.width = 120
        home_logo.height = 120
        top_spacer.height = 0
        bottom_spacer.height = 0
        page.update()
        time.sleep(1.2)

        # Phase 3: Reveal background
        dark_cover.opacity = 0
        page.update()
        time.sleep(0.6)

        # Phase 4: Cascade text
        welcome_text.opacity = 1
        page.update()
        time.sleep(0.25)

        fixit_title.opacity = 1
        page.update()
        time.sleep(0.25)

        subtitle.opacity = 1
        page.update()
        time.sleep(0.25)

        btn_wrapper.opacity = 1
        page.update()
        time.sleep(0.5)

        # Cleanup
        main_stack.controls.remove(dark_cover)
        page.update()

    # Background pan loop — continuous slow drift
    def pan_bg():
        step = 0
        time.sleep(4.5)
        while _alive:
            if step == 0:
                bg.offset = ft.Offset(0.06, 0.03)
                bg.scale = 1.3
            elif step == 1:
                bg.offset = ft.Offset(-0.04, 0.05)
                bg.scale = 1.25
            elif step == 2:
                bg.offset = ft.Offset(-0.06, -0.03)
                bg.scale = 1.32
            else:
                bg.offset = ft.Offset(0.04, -0.04)
                bg.scale = 1.25
            step = (step + 1) % 4
            try:
                page.update()
            except Exception:
                break
            time.sleep(12)

    threading.Thread(target=run_intro, daemon=True).start()
    threading.Thread(target=pan_bg, daemon=True).start()