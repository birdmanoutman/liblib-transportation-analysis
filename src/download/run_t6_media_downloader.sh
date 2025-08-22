#!/bin/bash
# T6 媒体下载器启动脚本

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python版本: $PYTHON_VERSION"
}

# 检查依赖
check_dependencies() {
    print_info "检查Python依赖..."
    
    cd "$PROJECT_ROOT"
    
    # 检查必要的包
    REQUIRED_PACKAGES=("boto3" "mysql.connector" "dotenv" "requests")
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            print_warning "缺少依赖包: $package"
            print_info "正在安装依赖..."
            pip3 install -r "$SCRIPT_DIR/requirements_t6.txt"
            break
        fi
    done
    
    print_success "依赖检查完成"
}

# 检查环境配置
check_environment() {
    print_info "检查环境配置..."
    
    cd "$PROJECT_ROOT"
    
    if [ ! -f ".env" ]; then
        print_error ".env 文件不存在"
        print_info "请创建 .env 文件并配置必要的环境变量"
        exit 1
    fi
    
    # 检查必要的环境变量
    source .env
    
    REQUIRED_VARS=("S3_ENDPOINT" "S3_BUCKET" "S3_ACCESS_KEY" "S3_SECRET_KEY")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "环境变量 $var 未设置"
            exit 1
        fi
    done
    
    print_success "环境配置检查完成"
}

# 运行测试
run_tests() {
    print_info "运行T6媒体下载器测试..."
    
    cd "$SCRIPT_DIR"
    
    if python3 test_t6_media_downloader.py; then
        print_success "测试通过"
        return 0
    else
        print_error "测试失败"
        return 1
    fi
}

# 运行演示
run_demo() {
    print_info "运行T6媒体下载器演示..."
    
    cd "$SCRIPT_DIR"
    
    if python3 demo_t6_media_downloader.py; then
        print_success "演示完成"
        return 0
    else
        print_warning "演示过程中发现问题"
        return 1
    fi
}

# 运行主程序
run_main() {
    print_info "启动T6媒体下载器..."
    
    cd "$SCRIPT_DIR"
    
    # 设置环境变量
    export MEDIA_ENV="${MEDIA_ENV:-dev}"
    
    print_info "运行环境: $MEDIA_ENV"
    
    # 运行主程序
    if python3 t6_media_downloader.py; then
        print_success "T6媒体下载器执行完成"
        return 0
    else
        print_error "T6媒体下载器执行失败"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "T6 媒体下载器启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -t, --test     运行测试"
    echo "  -d, --demo     运行演示"
    echo "  -e, --env      设置运行环境 (dev/test/prod)"
    echo "  -c, --check    检查环境和依赖"
    echo ""
    echo "示例:"
    echo "  $0                    # 运行主程序 (默认dev环境)"
    echo "  $0 -e prod            # 生产环境运行"
    echo "  $0 -t                 # 运行测试"
    echo "  $0 -d                 # 运行演示"
    echo "  $0 -c                 # 检查环境"
}

# 主函数
main() {
    print_info "T6 媒体下载器启动脚本"
    print_info "项目根目录: $PROJECT_ROOT"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--test)
                check_python
                check_dependencies
                check_environment
                run_tests
                exit $?
                ;;
            -d|--demo)
                check_python
                check_dependencies
                check_environment
                run_demo
                exit $?
                ;;
            -e|--env)
                export MEDIA_ENV="$2"
                shift 2
                ;;
            -c|--check)
                check_python
                check_dependencies
                check_environment
                print_success "环境检查完成"
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 默认运行主程序
    check_python
    check_dependencies
    check_environment
    run_main
}

# 运行主函数
main "$@"
